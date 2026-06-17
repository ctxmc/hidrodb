# BSD 2-Clause License

# Copyright (c) 2026, base

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from concurrent.futures import ThreadPoolExecutor, as_completed
from queue              import Queue
from threading          import Thread, Lock

from datetime import datetime, timedelta
from calendar import monthrange
from enum     import Enum, auto, StrEnum

import time
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import text, update

from database          import *
from hidro_webservices import *

class HidroJob(StrEnum):
    RAIN              = "Chuvas"
    DISCHARGE_SUMMARY = "ResumoDescarga"
    DISCHARGE_FLOW    = "CurvaDescarga"
    SEDIMENTS         = "Sedimentos"
    WATER_QUALITY     = "QualAgua"
    STAGE             = "Cotas"
    GRANULOMETRY      = "Granulometria"
    CROSS_SECTION     = "PerfilTransversal"

    def get_model(self):
        mapping = {
            HidroJob.RAIN:              Rain,
            HidroJob.DISCHARGE_SUMMARY: DischargeSummary,
            HidroJob.DISCHARGE_FLOW:    DischargeFlow,
            HidroJob.SEDIMENTS:         Sediments,
            HidroJob.WATER_QUALITY:     WaterQuality,
            HidroJob.STAGE:             Stage,
            HidroJob.GRANULOMETRY:      Granulometry,
            HidroJob.CROSS_SECTION:     CrossSection,
        }
        return mapping[self]

    def get_endpoint(self):
        mapping = {
            HidroJob.RAIN:              HidroEndpoint.RAIN,
            HidroJob.DISCHARGE_SUMMARY: HidroEndpoint.DISCHARGE_SUMMARY,
            HidroJob.DISCHARGE_FLOW:    HidroEndpoint.DISCHARGE_FLOW,
            HidroJob.SEDIMENTS:         HidroEndpoint.SEDIMENTS,
            HidroJob.WATER_QUALITY:     HidroEndpoint.WATER_QUALITY,
            HidroJob.STAGE:             HidroEndpoint.STAGE,
            HidroJob.GRANULOMETRY:      HidroEndpoint.GRANULOMETRY,
            HidroJob.CROSS_SECTION:     HidroEndpoint.CROSS_SECTION,
        }
        return mapping[self]

class JobStatus(Enum):
    PENDING   = auto()
    FAILED    = auto()
    INVALID   = auto()
    CORRUPTED = auto()
    COMPLETED = auto()

def get_token():
    logger.debug("Cheking Token.")
    client  = DatabaseConnection(client_path, DatabaseType.CLIENT)
    session = client.get_session()
    if (not session.query(Token).count()):
        logger.info("No Token present, requesting.")
        client_id, client_password = session.query(Credentials.ID, Credentials.Password).first()
        token, expires = request_token(client_id, client_password)
        session.add(Token(CredentialID=client_id, Token=token, Expires=expires))
        session.commit()
        return token
    else:
        (expires,) = session.query(Token.Expires).first()
        if datetime.now() < expires:
            logger.debug(f"Token is valid, continuing ({expires}).")
            (token,) = session.query(Token.Token).first()
            return token
        else:
            logger.info("Token expired, requesting new.")
            client_id, client_password = session.query(Credentials.ID, Credentials.Password).first()
            token, new_expires = request_token(client_id, client_password)
            logger.info("Aquired new token, updating.")
            update_expression = (
                update(Token).where(Token.Expires == expires)
                .values(Token=token, Expires=new_expires)
            )
            session.execute(update_expression)
            session.commit()
            logger.info("Token updated.")
            return token

def check_job(hidro_job):
    logger.info(f"Checking Job for {hidro_job}")
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    jobs_count = client_session.query(SeriesJobs).where(SeriesJobs.HidroTable == hidro_job).count()
    if not jobs_count:
        logger.info(f"Creating jobs for {hidro_job}")
        hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
        hidro_session = hidro_db.get_session()
        match hidro_job:
            case HidroJob.RAIN:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoRegistradorChuvaInicio,
                    Station.PeriodoRegistradorChuvaFim
                ).filter(Station.PeriodoRegistradorChuvaInicio.isnot(None)).all()
            case HidroJob.DISCHARGE_SUMMARY | HidroJob.DISCHARGE_FLOW:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoDescLiquidaInicio,
                    Station.PeriodoDescLiquidaFim
                ).filter(Station.PeriodoDescLiquidaInicio.isnot(None)).all()
            case HidroJob.SEDIMENTS:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInicio,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case HidroJob.WATER_QUALITY:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoQualAguaInicio,
                    Station.PeriodoQualAguaFim
                ).filter(Station.PeriodoQualAguaInicio.isnot(None)).all()
            case HidroJob.STAGE:
                sql = text("""
                SELECT 
                    Codigo, 
                    MIN(PeriodoInicio) AS PeriodoInicio, 
                    CASE 
                        WHEN MAX(CASE WHEN PeriodoFim IS NULL THEN 1 ELSE 0 END) = 1 
                        THEN NULL 
                        ELSE MAX(PeriodoFim) 
                    END AS PeriodoFim 
                FROM ( 
                    SELECT Codigo, PeriodoEscalaInicio AS PeriodoInicio, PeriodoEscalaFim AS PeriodoFim 
                    FROM Estacao WHERE PeriodoEscalaInicio IS NOT NULL 
                    UNION 
                    SELECT Codigo, PeriodoRegistradorNivelInicio, PeriodoRegistradorNivelFim 
                    FROM Estacao WHERE PeriodoRegistradorNivelInicio IS NOT NULL 
                ) combined 
                GROUP BY Codigo 
                """)
                stations_data = hidro_session.execute(sql).fetchall()
            case HidroJob.GRANULOMETRY:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInicio,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case HidroJob.CROSS_SECTION:
                stations_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInico,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case _:
                logger.debug(f"TODO: {hidro_job}")
                return
        hidro_session.close()
        hidro_db.close()
        client_db.close()
        client_session.close()
        create_jobs(stations_data, hidro_job)
        check_job(hidro_job)
    else:
        logger.debug("TODO: Update JOBS?")
        jobs = (client_session.query(
                    SeriesJobs.ID,
                    SeriesJobs.StationID,
                    SeriesJobs.FromDate,
                    SeriesJobs.ToDate
                ).filter(
                    SeriesJobs.Status.in_([JobStatus.FAILED.value, JobStatus.PENDING.value]),
                    SeriesJobs.HidroTable == hidro_job)
                .all())
        if (len(jobs) > 1):
            trigger_job(jobs, hidro_job)
        else:
            logger.info(f"No pending jobs for {hidro_job}")

def create_jobs(stations_data, hidro_job):
    jobs = []
    for station_code, start_date, end_date in stations_data:
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]
        for fmt in formats:
            try:
                start_date = datetime.strptime(start_date, fmt)
                break
            except Exception as e:
                continue
        if end_date is None:
            end_date = datetime.today() - timedelta(days=1)
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            for fmt in formats:
                try:
                    end_date = datetime.strptime(end_date, fmt)
                    break
                except Exception as e:
                    continue
        if start_date > datetime.today():
            logger.warning(f"Corrupted start date {start_date} for station {station_code}")
            jobs.append(SeriesJobs(
                StationID  = station_code,
                FromDate   = start_date,
                ToDate     = end_date,
                Status     = JobStatus.CORRUPTED.value,
                HidroTable = hidro_job
            ))
            continue
        total_years  = end_date.year - start_date.year
        current_year = start_date
        for count_year in range(1, total_years+1):
            next_year = current_year.replace(year=current_year.year+1)
            if next_year > end_date:
                next_year = end_date
            jobs.append(SeriesJobs(
                StationID  = station_code,
                FromDate   = current_year,
                ToDate     = next_year,
                Status     = JobStatus.PENDING.value,
                HidroTable = hidro_job
            ))
            current_year = next_year
    insert_jobs(jobs)
    logger.info(f"Created {len(jobs)} jobs for Hidro_Job {hidro_job}")

write_queue = Queue()
def trigger_job(jobs, hidro_job):
    logger.info(f"Initiating jobs for {hidro_job}")
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for job in jobs:
            # handle_job(job, hidro_job)
            executor.submit(handle_job, job, hidro_job)
        executor.shutdown(wait=True)
    write_queue.put((hidro_job, None, None, None, True))
    writer.join()

lock = Lock()
def handle_job(job_data, hidro_job):
    # TODO, jobs creates it own params?
    job_id, station_code, initial_date, final_date = job_data
    with lock:
        token = get_token()
    status, data = request_serial_data(token, hidro_job.get_endpoint(),
                                       station_code, initial_date, final_date)
    if status:
        status = JobStatus.COMPLETED
    else:
        status = JobStatus.FAILED

    match hidro_job:
        case HidroJob.RAIN:
            if status == JobStatus.COMPLETED:
                for index, entrie in enumerate(data):
                    if len(entrie) != 76:
                        data   = []
                        status = JobStatus.INVALID
                        logger.warning(f"Invalid entry at index {index}: {entrie}")
                        break
        case HidroJob.DISCHARGE_SUMMARY:
            if status == JobStatus.COMPLETED:
                for index, entrie in enumerate(data):
                    if (len(entrie) != 10):
                        data   = []
                        status = JobStatus.INVALID
                        logger.warning(f"Invalid entry at index {index}: {entrie}, status={status}")
                        break
        case HidroJob.DISCHARGE_FLOW:
            if status == JobStatus.COMPLETED:
                for index, entrie in enumerate(data):
                    if (len(entrie) != 18):
                        data   = []
                        status = JobStatus.INVALID
                        logger.warning(f"Invalid entry at index {index}: {entrie}, status={status}")
                        break

    match status:
        case JobStatus.COMPLETED:
            status_label = "Completed"
        case JobStatus.FAILED:
            status_label = "Failed"
        case JobStatus.INVALID:
            status_label = "Invalid"
    logger.debug(f"""[JOB {hidro_job} {job_id}]: {status_label} request for station {station_code} """
                 f"""on period ({initial_date})-({final_date})""")
    write_queue.put((hidro_job, job_id, status.value, data, False))

def db_writer():
    hidro_db = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    batch_buffer = {"jobs": [], "data": []}
    total_data    = 0
    total_jobs    = 0
    total_elapsed = 0
    while True:
        try:
            if write_queue.empty():
                time.sleep(0.1)
                continue
            hidro_job, job_id, status, data, stop_signal = write_queue.get()
            if stop_signal:
                total_elapsed += write_data(hidro_db, hidro_job,
                                            batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {hidro_job}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}"""
                            f"""Finished jobs for {hidro_job}""")
                break;
            batch_buffer["jobs"].append({'status': status, 'job_id': job_id})
            if len(data) > 0:
                batch_buffer["data"].extend(data)
            if len(batch_buffer["data"]) >= BATCH_SIZE:
                total_data    += len(batch_buffer["data"])
                total_jobs    += len(batch_buffer["jobs"])
                total_elapsed += write_data(hidro_db, hidro_job,
                                            batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {hidro_job}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}""")
                batch_buffer = {"jobs": [], "data": []}
        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")
            raise

def write_data(hidro_db, hidro_job, job_data, hidro_data):
    start_time = time.perf_counter()
    if len(hidro_data) > 1:
        logger.info(f"[WRITER {hidro_job}]: Inserting {len(hidro_data)} entries")
        match hidro_job:
            case HidroJob.WATER_QUALITY:
                water_quality = []
                water_status  = []
                for item in hidro_data:
                    water_quality.append(WaterQuality.from_json(item))
                    water_status.append(WaterQualityStatus.from_json(item))
                insert_hidro(hidro_db, water_quality)
                insert_hidro(hidro_db, water_status)
            case HidroJob.CROSS_SECTION:
                cross_section   = []
                v_cross_section = []
                current_id      = None
                for data in hidro_data:
                    data_id = data.get("Registro_ID")
                    if current_id == data_id:
                        continue
                    current_id = data_id
                    cross_section.append(CrossSection.from_json(data))
                    import re, ast;
                    verticals_str = re.sub(r'(\w+)=', r'"\1":', data.get("verticais"))
                    verticals     = ast.literal_eval(verticals_str)
                    v_cross_section.extend([VerticalCrossSection.from_json(v, current_id) for v in verticals])
                insert_hidro(hidro_db, cross_section,   True)
                insert_hidro(hidro_db, v_cross_section, True)
            case _:
                model_data = [hidro_job.get_model().from_json(entrie) for entrie in hidro_data]
                insert_hidro(hidro_db, model_data)
    if len(job_data) > 0:
        update_jobs(job_data)
        logger.info(f"[WRITER {hidro_job}]: Updated {len(job_data)} jobs")
    elapsed_time = time.perf_counter() - start_time
    logger.info(f"[WRITER {hidro_job}]: Inserted {len(hidro_data)} entries in {elapsed_time} seconds")
    return elapsed_time

def check_telemeter():
    TABLE = "Telemeter"
    logger.info(f"Checking Jobs for {TABLE}")
    jobs_db = DatabaseConnection(jobs_path, DatabaseType.JOBS)
    jobs_session = jobs_db.get_session()
    count_jobs_sql = text(f"SELECT COUNT(*) FROM {TABLE}")
    jobs_count = jobs_session.execute(count_jobs_sql).fetchone()[0]
    if (not jobs_count):
        logger.info(f"Creating jobs for {TABLE}")
        sql = text(
            "SELECT Codigo, PeriodoTelemetricaInicio, PeriodoTelemetricaFim "
            "FROM Estacao WHERE PeriodoTelemetricaInicio IS NOT NULL"
        )
        hidro = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
        hidro_session = hidro.get_session()
        stations_data = hidro_session.execute(sql).fetchall()
        hidro.close()
        jobs  = []
        for station_code, start_date, end_date in stations_data:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f")
            if end_date is None:
                end_date = datetime.today() - timedelta(days=1)
                end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f")
            if start_date > datetime.today():
                logger.warning(f"Corrupted start date {start_date} for station {station_code}")
                jobs.append({
                    'StationID': station_code,
                    'Date':      start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'Interval':  0,
                    'Status':    JobStatus.CORRUPTED.value
                })
                continue
            total_years  = end_date.year - start_date.year
            total_months = total_years * 12 + (end_date.month - start_date.month)
            current      = start_date
            while current <= end_date:
                month   = current.month + 1
                year    = current.year + (month - 1) // 12
                month   = ((month - 1) % 12) + 1
                max_day = monthrange(year, month)[1]
                day     = min(current.day, max_day)
                current = current.replace(year=year, month=month, day=day)
                jobs.append({
                    'StationID': station_code,
                    'Date':      current.strftime("%Y-%m-%d %H:%M:%S"),
                    'Interval':  0,
                    'Status':    JobStatus.PENDING.value
                })
        sql = text(f"""INSERT INTO {TABLE} (StationID, Date, Interval, Status)"""
                   """VALUES (:StationID, :Date, :Interval, :Status)""")
        insert_jobs(jobs, sql)
        logger.info(f"Created {len(jobs)} jobs for Table {TABLE}")
        check_telemeter()
    else:
        logger.debug("TODO: Update JOBS?")
        get_jobs_sql = text("""SELECT ID, StationID, Date, Interval """
                            f"""FROM {TABLE} WHERE Status = {JobStatus.FAILED.value} """
                            f"""OR                 Status = {JobStatus.PENDING.value}""")
        jobs = jobs_session.execute(get_jobs_sql).fetchall()
        trigger_telemeter(jobs, TABLE)

def trigger_telemeter(jobs, job_name):
    logger.info(f"Initiating jobs for {job_name}")
    for job in jobs:
        job_id, station_code, date, interval = job
        token = get_token()
        status, data = request_telemeter_data(token, HidroEndpoint.TELEMETER, station_code, date)
        if status:
            status = JobStatus.COMPLETED
        else:
            status = JobStatus.FAILED
        match status:
            case JobStatus.COMPLETED:
                status_label = "Completed"
            case JobStatus.FAILED:
                status_label = "Failed"
        logger.debug(f"""[JOB {job_name} {job_id}]: {status_label} """
                     f"""request for station {station_code} on period {date}""")
