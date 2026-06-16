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

from sqlalchemy import text

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
    result  = session.execute(text("SELECT COUNT(*) FROM Token"))
    if (not result.fetchone()[0]):
        logger.info("No Token present, requesting.")
        result = session.execute(text("SELECT ID FROM Credentials"))
        client_id = result.fetchone()[0]
        result = session.execute(text("SELECT Password FROM Credentials"))
        client_password = result.fetchone()[0]
        token, expires = request_token(client_id, client_password)
        expires = expires.strftime("%Y-%m-%d %H:%M:%S")
        insert_token_sql = f"INSERT INTO Token (Token, Expires) VALUES ('{token}', '{expires}')"
        session.execute(text(insert_token_sql))
        session.commit()
        return token
    else:
        result = session.execute(text("SELECT Expires FROM Token"))
        expires_ISOND = result.fetchone()[0]
        expires_datetime = datetime.strptime(expires_ISOND, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expires_datetime:
            logger.debug(f"Token is valid, continuing ({expires_datetime}).")
            result = session.execute(text("SELECT Token FROM Token"))
            return result.fetchone()[0]
        else:
            logger.info("Token expired, requesting new.")
            result = session.execute(text("SELECT ID FROM Credentials"))
            client_id = result.fetchone()[0]
            result = session.execute(text("SELECT Password FROM Credentials"))
            client_password = result.fetchone()[0]
            token, expires = request_token(client_id, client_password)
            logger.info("Aquired new token, updating.")
            update_token_sql = text(f"""UPDATE [Token] SET [Token] = '{token}', """
                                    f"""[Expires] = '{expires}' """
                                    f"""WHERE [Expires] = '{expires_ISOND}'""")
            session.execute(update_token_sql)
            session.commit()
            logger.info("Token updated.")
            return token

def check_job(job_name):
    logger.info(f"Checking Job for {job_name}")
    jobs_db = DatabaseConnection(jobs_path, DatabaseType.JOBS)
    jobs_session = jobs_db.get_session()
    count_jobs_sql = text(f"SELECT COUNT(*) FROM {job_name}")
    jobs_count = jobs_session.execute(count_jobs_sql).fetchone()[0]
    if (not jobs_count):
        logger.info(f"Creating jobs for {job_name}")
        match job_name:
            case "Chuvas":
                sql = text(
                    "SELECT Codigo, PeriodoRegistradorChuvaInicio, PeriodoRegistradorChuvaFim "
                    "FROM Estacao WHERE PeriodoRegistradorChuvaInicio IS NOT NULL"
                )
            case "ResumoDescarga" | "CurvaDescarga":
                sql = text(
                    "SELECT Codigo, PeriodoDescLiquidaInicio, PeriodoDescLiquidaFim "
                    "FROM Estacao WHERE PeriodoDescLiquidaInicio IS NOT NULL"
                )
            case "Sedimentos":
                sql = text(
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case "QualAgua":
                sql = text(
                    "SELECT Codigo, PeriodoQualAguaInicio, PeriodoQualAguaFim "
                    "FROM Estacao WHERE PeriodoQualAguaInicio IS NOT NULL"
                )
            case "Cotas":
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
            case "Granulometria":
                sql = text(
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case "PerfilTransversal":
                sql = text(
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case _:
                logger.debug(f"TODO: {job_name}")
                return
        hidro = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
        hidro_session = hidro.get_session()
        stations_data = hidro_session.execute(sql).fetchall()
        hidro.close()
        create_jobs(stations_data, job_name)
        jobs_db.close()
        check_job(job_name)
    else:
        logger.debug("TODO: Update JOBS?")
        get_jobs_sql = text("""SELECT ID, StationID, FromDate, ToDate """
                            f"""FROM {job_name} WHERE Status = {JobStatus.FAILED.value} """
                            f"""OR                    Status = {JobStatus.PENDING.value}""")
        jobs = jobs_session.execute(get_jobs_sql).fetchall()
        if (len(jobs) > 1):
            trigger_job(jobs, job_name)
        else:
            logger.info(f"No pending jobs for {job_name}")

def create_jobs(stations_data, table):
    jobs = []
    for station_code, start_date, end_date in stations_data:
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]
        for fmt in formats:
            try:
                start_date = datetime.strptime(start_date, fmt)
                break
            except ValueError:
                continue
        if end_date is None:
            end_date = datetime.today() - timedelta(days=1)
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            for fmt in formats:
                try:
                    end_date = datetime.strptime(end_date, fmt)
                    break
                except ValueError:
                    continue
        if start_date > datetime.today():
            logger.warning(f"Corrupted start date {start_date} for station {station_code}")
            jobs.append({
                'StationID': station_code,
                'FromDate':  start_date.strftime("%Y-%m-%d %H:%M:%S"),
                'ToDate':    end_date.strftime("%Y-%m-%d %H:%M:%S"),
                'Status':    JobStatus.CORRUPTED.value
            })
            continue
        total_years  = end_date.year - start_date.year
        current_year = start_date
        for count_year in range(1, total_years+1):
            next_year = current_year.replace(year=current_year.year+1)
            if next_year > end_date:
                next_year = end_date
            jobs.append({
                'StationID': station_code,
                'FromDate':  current_year.strftime("%Y-%m-%d %H:%M:%S"),
                'ToDate':    next_year.strftime("%Y-%m-%d %H:%M:%S"),
                'Status':    JobStatus.PENDING.value
            })
            current_year = next_year
    sql = text(f"""INSERT INTO {table} (StationID, FromDate, ToDate, Status)"""
               """VALUES (:StationID, :FromDate, :ToDate, :Status)""")
    insert_jobs(jobs, sql)
    logger.info(f"Created {len(jobs)} jobs for Table {table}")

write_queue = Queue()
def trigger_job(jobs, job_name):
    logger.info(f"Initiating jobs for {job_name}")
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    MAX_WORKERS=10
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for job in jobs:
            executor.submit(handle_job, job, job_name)
        executor.shutdown(wait=True)
    write_queue.put((job_name, None, None, None, True))
    writer.join()

lock = Lock()
def handle_job(job_data, job_name):
    job_id, station_code, initial_date, final_date = job_data
    with lock:
        token = get_token()
    match job_name:
        case "Chuvas":
            status, data = request_serial_data(token, HidroEndpoint.RAIN,
                                                station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 76):
                        data   = []
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [Rain.from_json(entrie) for entrie in data]
            else:
                status = JobStatus.FAILED
        case "ResumoDescarga":
            status, data = request_serial_data(token, HidroEndpoint.DISCHARGE_SUMMARY,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 10):
                        data   = []
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [DischargeSummary.from_json(entrie) for entrie in data]
            else:
                status = JobStatus.FAILED
        case "Sedimentos":
            status, data = request_serial_data(token, HidroEndpoint.SEDIMENTS,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                data = [Sediments.from_json(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "QualAgua":
            status, data = request_serial_data(token, HidroEndpoint.WATER_QUALITY,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
            else:
                status = JobStatus.FAILED
        case "Cotas":
            status, data = request_serial_data(token, HidroEndpoint.STAGE,
                                            station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                data = [Stage.from_json(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "CurvaDescarga":
            status, data = request_serial_data(token, HidroEndpoint.DISCHARGE_FLOW,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 18):
                        data   = []
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [DischargeFlow.from_json(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "Granulometria":
            status, data = request_serial_data(token, HidroEndpoint.GRANULOMETRY,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                data = [Granulometry.from_json(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "PerfilTransversal":
            status, data = request_serial_data(token, HidroEndpoint.CROSS_SECTION,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
            else:
                status = JobStatus.FAILED
    match status:
        case JobStatus.COMPLETED:
            status_label = "Completed"
        case JobStatus.FAILED:
            status_label = "Failed"
        case JobStatus.INVALID:
            status_label = "Invalid"
    logger.debug(f"""[JOB {job_name} {job_id}]: {status_label} request for station {station_code} """
                 f"""on period ({initial_date})-({final_date})""")
    write_queue.put((job_name, job_id, status.value, data, False))

def db_writer():
    hidro_db = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    batch_buffer = {"jobs": [], "data": []}
    BATCH_SIZE   = 10000
    total_data    = 0
    total_jobs    = 0
    total_elapsed = 0
    while True:
        try:
            if write_queue.empty():
                time.sleep(0.1)
                continue
            job_name, job_id, status, data, stop_signal = write_queue.get()
            if stop_signal:
                total_elapsed += write_data(hidro_db, job_name,
                                            batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {job_name}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}"""
                            f"""Finished jobs for {job_name}""")
                break;
            batch_buffer["jobs"].append({'status': status, 'job_id': job_id})
            if len(data) > 0:
                batch_buffer["data"].extend(data)
            if len(batch_buffer["data"]) >= BATCH_SIZE:
                total_data    += len(batch_buffer["data"])
                total_jobs    += len(batch_buffer["jobs"])
                total_elapsed += write_data(hidro_db, job_name,
                                            batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {job_name}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}""")
                batch_buffer = {"jobs": [], "data": []}
        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")

def write_data(hidro_db, job_name, job_data, hidro_data):
    start_time = time.perf_counter()
    if len(hidro_data) > 0:
        logger.info(f"[WRITER {job_name}]: Inserting {len(hidro_data)} entries")
        match job_name:
            case "Chuvas":
                insert_hidro(hidro_db, hidro_data)
            case "ResumoDescarga":
                insert_hidro(hidro_db, hidro_data)
            case "Sedimentos":
                insert_hidro(hidro_db, hidro_data)
            case "Cotas":
                insert_hidro(hidro_db, hidro_data)
            case "CurvaDescarga":
                insert_hidro(hidro_db, hidro_data)
            case "Granulometria":
                insert_hidro(hidro_db, hidro_data)
            case "QualAgua":
                water_quality = []
                water_status  = []
                for item in hidro_data:
                    water_quality.append(WaterQuality.from_json(item))
                    water_status.append(WaterQualityStatus.from_json(item))
                insert_hidro(hidro_db, water_quality)
                insert_hidro(hidro_db, water_status)
            case "PerfilTransversal":
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
    if len(job_data) > 0:
        update_jobs(job_name, job_data)
        logger.info(f"[WRITER {job_name}]: Updated {len(job_data)} jobs")
    elapsed_time = time.perf_counter() - start_time
    logger.info(f"[WRITER {job_name}]: Inserted {len(hidro_data)} entries in {elapsed_time} seconds")
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
