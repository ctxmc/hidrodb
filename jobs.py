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

    def __iter__(self):
        return iter((self.station_code, self.start_date, self.end_date))

def get_token() -> str:
    """Authenticate and return access token.
    Returns: Valid token for requesition
    """
    logger.verbose("Cheking Token.")
    client  = DatabaseConnection(client_path, DatabaseType.CLIENT)
    session = client.get_session()
    if (not session.query(Token).count()):
        logger.verbose("No Token present, requesting.")
        client_id, client_password = session.query(Credentials.ID, Credentials.Password).first()
        token, expires = request_token(client_id, client_password)
        session.add(Token(CredentialID=client_id, Token=token, Expires=expires))
        session.commit()
        return token
    else:
        (expires,) = session.query(Token.Expires).first()
        if datetime.now() < expires:
            logger.verbose(f"Token is valid, continuing ({expires}).")
            (token,) = session.query(Token.Token).first()
            return token
        else:
            logger.verbose("Token expired, requesting new.")
            client_id, client_password = session.query(Credentials.ID, Credentials.Password).first()
            token, new_expires = request_token(client_id, client_password)
            logger.verbose("Aquired new token, updating.")
            from sqlalchemy import update;
            update_expression = (
                update(Token).where(Token.Expires == expires)
                .values(Token=token, Expires=new_expires)
            )
            session.execute(update_expression)
            session.commit()
            logger.verbose("Token updated.")
            return token


def check_resource(resource: HidroResource) -> None:
    hidro_db = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    session  = hidro_db.get_session()
    model    = resource.get_model()
    endpoint = resource.get_endpoint()
    logger.verbose(f"Checking {resource}.")
    if (not session.query(model).count()):
        logger.info(f"{resource} has no Entries, requesting data.")
        match resource:
            case HidroResource.STATION:
                items = []
                states = session.query(State).filter(State.CodigoIBGE.isnot(None)).all()
                for state in states:
                    token = get_token()
                    if (token):
                        params = {"Unidade Federativa": f"{state.Sigla}"}
                        success, items_uf = request_data(token, endpoint, params,
                                                         save_response, load_response)
                        items.extend(items_uf)
                entries = [model.from_json(item) for item in items]
                entries.EstadoCodigo = state.Codigo
            case _:
                token = get_token()
                if (token):
                    success, items = request_data(token, endpoint, {}, save_response, load_response)
                    entries = [model.from_json(item) for item in items]
        insert_hidro(hidro_db, entries)
    else:
        logger.verbose(f"[TODO] {resource} has Entries")
    session.close()
    hidro_db.close()


def check_series_job(job_config: JobConfig) -> None:
    logger.trace(f"Checking Job for {job_config}")
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    jobs_count = client_session.query(SeriesJobs).where(SeriesJobs.HidroTable == job_config).count()
    if not jobs_count:
        logger.info(f"Creating jobs for {job_config}")
        hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
        hidro_session = hidro_db.get_session()
        match job_config:
            case JobConfig.RAIN:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoRegistradorChuvaInicio,
                    Station.PeriodoRegistradorChuvaFim
                ).filter(Station.PeriodoRegistradorChuvaInicio.isnot(None)).all()
            case JobConfig.DISCHARGE_SUMMARY | JobConfig.DISCHARGE_FLOW | JobConfig.CROSS_SECTION:
                db_data =  hidro_session.query(
                    Station.Codigo,
                    Station.PeriodoDescLiquidaInicio,
                    Station.PeriodoDescLiquidaFim
                ).filter(Station.PeriodoDescLiquidaInicio.isnot(None)).all()
            case JobConfig.SEDIMENTS | JobConfig.GRANULOMETRY:
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
                from sqlalchemy import text
                sql = text("""
                SELECT 
                    Codigo, 
                    MIN(PeriodoInicio) AS PeriodoInicio, 
                    MIN(PeriodoFim)    AS PeriodoFim
                FROM (
                    SELECT Codigo, PeriodoEscalaInicio AS PeriodoInicio, PeriodoEscalaFim AS PeriodoFim
                    FROM Estacao WHERE PeriodoEscalaInicio IS NOT NULL
                    UNION
                    SELECT Codigo, PeriodoRegistradorNivelInicio, PeriodoRegistradorNivelFim
                    FROM Estacao WHERE PeriodoRegistradorNivelInicio IS NOT NULL
                ) combined
                GROUP BY Codigo;
                """)
                db_data = hidro_session.execute(sql).fetchall()
        hidro_session.close()
        hidro_db.close()
        client_db.close()
        client_session.close()
        stations_data = [SerieStationData(code, start, end) for code, start, end in db_data]
        create_series_jobs(stations_data, job_config)
        check_series_job(job_config)
    else:
        logger.verbose("[TODO]: Update JOBS")
        jobs = (client_session.query(SeriesJobs)
                .filter(
                    SeriesJobs.Status.in_([JobStatus.FAILED.value, JobStatus.PENDING.value]),
                    SeriesJobs.HidroTable == job_config)
                .all())
        if (len(jobs) > 1):
            trigger_job(jobs, job_config)
        else:
            logger.info(f"No pending jobs for {job_config}")


def create_series_jobs(stations_data: List[SerieStationData], job_config: JobConfig) -> None:
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
                HidroTable = job_config
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
                HidroTable = job_config
            ))
            current_year = next_year
    insert_jobs(jobs)
    logger.info(f"Created {len(jobs)} jobs for Job_Config {job_config}")


write_queue = Queue()
def trigger_job(jobs: HidroJob, job_config: JobConfig) -> None:
    logger.info(f"Initiating {len(jobs)} jobs for {job_config}")
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for job in jobs:
            executor.submit(handle_job, job, job_config)
        executor.shutdown(wait=True)
    write_queue.put((job_config, None, None, True))
    writer.join()


lock = Lock()
def handle_job(job: HidroJob, job_config: JobConfig) -> None:
    with lock:
        token = get_token()
    success, data = request_data(token, job_config.get_endpoint(), job.to_params(),
                                 save_response, load_response)

    if success:
        job, data = validate_data(job_config, data, job)
    else:
        job.Status = JobStatus.FAILED

    logger.trace(f"""[JOB {job_config} {job.ID}]: {job.Status.get_label()} """
                 f"""request for station {job.StationID} """
                 f"""on period ({job.FromDate})-({job.ToDate})""")
    write_queue.put((job_config, job, data, False))


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

            job_config, job, data, stop_signal = write_queue.get()

            if job:
                batch_buffer["jobs"].append(job)
            if data and len(data) > 0:
                batch_buffer["data"].extend(data)

            if len(batch_buffer["data"]) >= BATCH_SIZE or stop_signal:
                total_data    += len(batch_buffer["data"])
                total_jobs    += len(batch_buffer["jobs"])
                total_elapsed += write_data(hidro_db, job_config,
                                            batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {job_config}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}""")
                batch_buffer = {"jobs": [], "data": []}

            if stop_signal:
                logger.info(f"""Finished jobs for {job_config}""")
                break;

        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")
            raise

def write_data(hidro_db: DatabaseConnection, job_config: JobConfig, jobs: List[HidroJob], hidro_data: dict) -> float:        
    start_time = time.perf_counter()
    if len(hidro_data) > 0:
        logger.trace(f"[WRITER {job_config}]: Inserting {len(hidro_data)} entries")
        model_data = data_to_model_orm(job_config, hidro_data)
        has_id = True if job_config == JobConfig.CROSS_SECTION else False
        insert_hidro(hidro_db, model_data, has_id)
    if len(jobs) > 0:
        update_jobs(jobs)
        logger.trace(f"[WRITER {job_config}]: Updated {len(jobs)} jobs")
    elapsed_time = time.perf_counter() - start_time
    logger.trace(f"[WRITER {job_config}]: Inserted {len(hidro_data)} entries in {elapsed_time} seconds")
    return elapsed_time


def validate_data(job_config: JobConfig, items: dict, job: HidroJob) -> (HidroJob, dict):
    #TODO: VALIDATE EACH JSON KEY FOR EACH TABLE?
    job.Status = JobStatus.COMPLETED

    match job_config:
        case JobConfig.RAIN:
            dict_len = 76
        case JobConfig.DISCHARGE_SUMMARY:
            dict_len = 10
        case JobConfig.DISCHARGE_FLOW:
            dict_len = 18
        case JobConfig.STAGE:
            dict_len = 78
        case JobConfig.GRANULOMETRY:
            dict_len = 117
        case JobConfig.CROSS_SECTION:
            dict_len = 18
        case _:
            #TODO: CHECK LEN FOR EVERY TABLE?
            return (status, items)

    for item in items:
        if (len(item) != dict_len):
            items   = []
            job.Status = JobStatus.INVALID
            logger.verbose(f"[VALIDATE JOB {job_id}] Invalid item: {item}")
            break

    return (job, items)


def data_to_model_orm(job_config: JobConfig, hidro_data: dict):
    model_data = []
    match job_config:
        case JobConfig.WATER_QUALITY:
            for item in hidro_data:
                model_data.append(WaterQuality.from_json(item))
                model_data.append(WaterQualityStatus.from_json(item))
        case JobConfig.CROSS_SECTION:
            current_id      = None
            for item in hidro_data:
                item_id = item.get("Registro_ID")
                if current_id != item_id:
                    current_id = item_id
                    model_data.append(job_config.get_model().from_json(item))
                model_data.append(VerticalCrossSection.from_json(item, current_id))
        case _:
            for data in hidro_data:
                model_data.append(job_config.get_model().from_json(data))
    return model_data
