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

from concurrent.futures import ThreadPoolExecutor
from queue              import Queue
from threading          import Thread, Lock

from datetime import datetime, timedelta
from enum     import Enum, auto

import time
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import text, update

from database          import *
from hidro_webservices import *
from config            import *
from dataclasses       import dataclass

class JobStatus(Enum):
    PENDING   = auto()
    FAILED    = auto()
    INVALID   = auto()
    CORRUPTED = auto()
    COMPLETED = auto()

    def get_label(self):
        mapping = {
            JobStatus.PENDING:   "Pending",
            JobStatus.FAILED:    "Failed",
            JobStatus.INVALID:   "Invalid",
            JobStatus.CORRUPTED: "Corrupted",
            JobStatus.COMPLETED: "Completed"
        }
        return mapping[self]

@dataclass
class SerieStationData:
    station_code: int
    start_date:   DateTime
    end_date:     DateTime

def get_token() -> bool:
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


def check_resource(resource: HidroResource) -> None:
    hidro_db = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    session  = hidro_db.get_session()
    model    = resource.get_model()
    endpoint = resource.get_endpoint()
    if (not session.query(model).count()):
        logger.info(f"{resource} has no Entries, requesting data")
        token = get_token()
        if (token):
            match resource:
                case HidroResource.STATION:
                    entries = []
                    states_uf = session.query(State.Sigla).filter(State.CodigoIBGE.isnot(None)).all()
                    for (UF,) in states_uf:
                        token = get_token()
                        if (token):
                            params = {"Unidade Federativa": f"{UF}"}
                            items = request_data(token, endpoint, params)
                            entries.extend([model.from_json(item) for item in items])
                case _:
                    entries = [model.from_json(item) for item in request_data(token, endpoint)]
            insert_hidro(hidro_db, entries)
    else:
        logger.debug(f"{resource} has Entries; TODO")
    session.close()
    hidro_db.close()


def check_job(hidro_job: JobConfig) -> None:
    logger.info(f"Checking Job for {hidro_job}")
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    jobs_count = client_session.query(SeriesJobs).where(SeriesJobs.HidroTable == hidro_job).count()
    if not jobs_count:
        logger.info(f"Creating jobs for {hidro_job}")
        hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
        hidro_session = hidro_db.get_session()
        match hidro_job:
            case JobConfig.RAIN:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoRegistradorChuvaInicio,
                    Station.PeriodoRegistradorChuvaFim
                ).filter(Station.PeriodoRegistradorChuvaInicio.isnot(None)).all()
            case JobConfig.DISCHARGE_SUMMARY | JobConfig.DISCHARGE_FLOW:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoDescLiquidaInicio,
                    Station.PeriodoDescLiquidaFim
                ).filter(Station.PeriodoDescLiquidaInicio.isnot(None)).all()
            case JobConfig.SEDIMENTS:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInicio,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case JobConfig.WATER_QUALITY:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoQualAguaInicio,
                    Station.PeriodoQualAguaFim
                ).filter(Station.PeriodoQualAguaInicio.isnot(None)).all()
            case JobConfig.STAGE:
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
                db_data = hidro_session.execute(sql).fetchall()
            case JobConfig.GRANULOMETRY:
                db_data = hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInicio,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case JobConfig.CROSS_SECTION:
                db_data = hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoSedimentosInicio,
                    Station.PeriodoSedimentosFim
                ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
            case _:
                logger.debug(f"TODO: {hidro_job}")
                return
        hidro_session.close()
        hidro_db.close()
        client_db.close()
        client_session.close()
        stations_data = [SerieStationData(code, start, end) for code, start, end in db_data]
        create_series_jobs(stations_data, hidro_job)
        check_job(hidro_job)
    else:
        logger.debug("TODO: Update JOBS?")
        jobs = (client_session.query(SeriesJobs)
                .filter(
                    SeriesJobs.Status.in_([JobStatus.FAILED.value, JobStatus.PENDING.value]),
                    SeriesJobs.HidroTable == hidro_job)
                .all())
        if (len(jobs) > 1):
            trigger_job(jobs, hidro_job)
        else:
            logger.info(f"No pending jobs for {hidro_job}")


def create_series_jobs(stations_data: SerieStationData, hidro_job: JobConfig) -> None:
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
def trigger_job(jobs: SeriesJobs, hidro_job: JobConfig) -> None:
    logger.info(f"Initiating {len(jobs)} jobs for {hidro_job}")
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for job in jobs:
            executor.submit(handle_job, job, hidro_job)
        executor.shutdown(wait=True)
    write_queue.put((hidro_job, None, None, None, True))
    writer.join()


lock = Lock()
def handle_job(job: SeriesJobs, hidro_job: JobConfig) -> None:
    with lock:
        token = get_token()
    success, data = request_serial_data(token, hidro_job.get_endpoint(), job.to_params())
    if success:
        status, data = validate_data(hidro_job, data)
    else:
        status = JobStatus.FAILED

    logger.debug(f"""[JOB {hidro_job} {job.ID}]: {status.get_label()} """
                 f"""request for station {job.StationID} """
                 f"""on period ({job.FromDate})-({job.ToDate})""")
    write_queue.put((hidro_job, job.ID, status.value, data, False))


def db_writer() -> None:
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


def write_data(hidro_db: DatabaseConnection, hidro_job: JobConfig, job_data: dict, hidro_data: dict) -> float:
    start_time = time.perf_counter()
    if len(hidro_data) > 1:
        logger.info(f"[WRITER {hidro_job}]: Inserting {len(hidro_data)} entries")
        model_data = data_to_model_orm(hidro_job, hidro_data)
        insert_hidro(hidro_db, model_data)
    if len(job_data) > 0:
        update_jobs(job_data)
        logger.info(f"[WRITER {hidro_job}]: Updated {len(job_data)} jobs")
    elapsed_time = time.perf_counter() - start_time
    logger.info(f"[WRITER {hidro_job}]: Inserted {len(hidro_data)} entries in {elapsed_time} seconds")
    return elapsed_time


def validate_data(hidro_job: JobConfig, items: dict) -> (JobStatus, dict):
    status = JobStatus.COMPLETED

    match hidro_job:
        case JobConfig.RAIN:
            dict_len = 76
        case JobConfig.DISCHARGE_SUMMARY:
            dict_len = 10
        case JobConfig.DISCHARGE_FLOW:
            dict_len = 18
        case _:
            return (status, data)

    for item in items:
        if (len(item) != dict_len):
            items   = []
            status = JobStatus.INVALID
            logger.warning(f"[VALIDATE] Invalid item: {item}")
            break

    return (status, items)


def data_to_model_orm(hidro_job: JobConfig, hidro_data: dict):
    model_data = []
    match hidro_job:
        case JobConfig.WATER_QUALITY:
            for item in hidro_data:
                model_data.append(WaterQuality.from_json(item))
                model_data.append(WaterQualityStatus.from_json(item))
        case JobConfig.CROSS_SECTION:
            current_id      = None
            for data in hidro_data:
                data_id = data.get("Registro_ID")
                if current_id == data_id:
                    continue
                current_id = data_id
                model_data.append(hidro_job.get_model().from_json(data))
                verticals_str = re.sub(r'(\w+)=', r'"\1":', data.get("verticais"))
                verticals     = ast.literal_eval(verticals_str)
                model_data.extend([VerticalCrossSection.from_json(v, current_id) for v in verticals])

        case _:
            for data in hidro_data:
                model_data.append(hidro_job.get_model().from_json(data))
    return model_data
