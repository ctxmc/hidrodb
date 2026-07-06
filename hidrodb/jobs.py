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

"""
Provides routines to request and sync data on database.
"""

import logging, time
logger = logging.getLogger(__name__)

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading          import Thread, Lock
from queue              import Queue

from datetime    import datetime, timedelta
from enum        import Enum, auto, StrEnum
from dataclasses import dataclass

from hidrodb.database    import *
from hidrodb.webservices import *

MAX_WORKERS = None
BATCH_SIZE  = None

class JobConfig:
    # """ TODO """

    class Base(StrEnum):
        """ Enum to hold basic resources data that does not require Threads. """

        BASIN             = "Bacia"
        SUB_BASIN         = "SubBacia"
        ENTITY            = "Entidade"
        TOWNSHIP          = "Municipio"
        RIVER             = "Rio"
        STATE             = "Estado"
        STATION           = "Estacao"

    class Series(StrEnum):
        """ Enum to hold Hidro Jobs that will run with threads. """

        RAIN              = "Chuvas"
        DISCHARGE_SUMMARY = "ResumoDescarga"
        DISCHARGE_FLOW    = "CurvaDescarga"
        SEDIMENTS         = "Sedimentos"
        WATER_QUALITY     = "QualAgua"
        STAGE             = "Cotas"
        GRANULOMETRY      = "Granulometria"
        CROSS_SECTION     = "PerfilTransversal"
        FLOW_RATE         = "Vazoes"

    class Status(Enum):
        PENDING   = auto()
        FAILED    = auto()
        INVALID   = auto()
        CORRUPTED = auto()
        COMPLETED = auto()


@dataclass
class SerieStationData:
    """ Data class to receive Series Job data when starting a job."""

    station_code: int
    """ Station code which data will be requested."""

    start_date:   DateTime
    """ Start date which data will be requested"""

    end_date:     DateTime
    """ End date which data will be requested"""

    def __iter__(self):
        return iter((self.station_code, self.start_date, self.end_date))

@dataclass
class QueueData:

    job_config:  JobConfig
    job:         HidroJob
    items:       dict
    worker_time: float
    stop_signal: bool

    def __iter__(self):
        return iter((
            self.job_config,
            self.job,
            self.items,
            self.worker_time,
            self.stop_signal
        ))


from typing import Optional
_token_cache: Optional[Token] = None
"""Private Token global to control expiration time."""

def get_token() -> Token.Token:
    """Authenticate and return access token.
    
    :returns: Valid token for requesition
    """

    global _token_cache
    if _token_cache is None:
        _token_cache = get_token_model()

    if _token_cache is not None and datetime.now() < _token_cache.Expires:
        logger.verbose(f"Token is valid. ({_token_cache.Expires})")
        return _token_cache.Token

    logger.info("No valid token present, requesting.")
    credentials = get_credentials()
    token, expires = request_token(credentials.ID, credentials.Password)
    if _token_cache is None:
        _token_cache = Token()
    _token_cache.Token   = token
    _token_cache.Expires = expires

    if count_client(Token):
        update_token(_token_cache.RegistroID, token, expires)
    else:
        add_token(credentials.ID, token, expires)

    logger.info("Token acquired and cached.")
    return token


def check_base_job(job_config: JobConfig.Base) -> None:
    """Checks each HidroJob and request/update them.

    :param job: Current Job to check, insert and update.
    :returns: Nothing.
    """

    filters = create_job_filters(job_config, None, last_check=False)
    if not count_job(job_config, filters):
        logger.info(f"Creating jobs for {job_config}.")
        job_model = get_job_model(job_config)
        jobs = []
        match job_config:
            case JobConfig.Base.STATION:
                for state in get_states():
                    job = job_model(
                        HidroTable = job_config,
                        Status     = JobConfig.Status.PENDING.value,
                        UF         = state.Sigla
                    )
                    jobs.append(job)
            case _:
                job = job_model(
                    HidroTable = job_config,
                    Status     = JobConfig.Status.PENDING.value
                )
                jobs.append(job)
        insert_jobs(jobs)
        check_base_job(job_config)
    else:
        status  = [JobConfig.Status.FAILED.value, JobConfig.Status.PENDING.value]
        filters = create_job_filters(job_config, status, last_check=True)
        count   = count_job(job_config, filters)
        if count:
            logger.info(f"Initiating jobs for {job_config}")
            trigger_job(job_config, filters)
        else:
            logger.info(f"No pending jobs for {job_config}.\n")


def check_series_job(job_config: JobConfig) -> None:
    """Checks an JobConfig.
    Create jobs if there is no entries and start pending jobs requisition.
    """

    filters = create_job_filters(job_config, None, last_check=False)
    if not count_job(job_config, filters):
        logger.info(f"Creating jobs for {job_config}")
        match job_config:
            case JobConfig.Series.RAIN:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_rain_period()]
            case (JobConfig.Series.DISCHARGE_SUMMARY | JobConfig.Series.DISCHARGE_FLOW |
                  JobConfig.Series.CROSS_SECTION     | JobConfig.Series.FLOW_RATE):
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_discharge_period()]
            case JobConfig.Series.SEDIMENTS | JobConfig.Series.GRANULOMETRY:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_sediments_period()]
            case JobConfig.Series.WATER_QUALITY:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_water_period()]
            case JobConfig.Series.STAGE:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_stage_period()]
        create_series_jobs(stations_data, job_config)
        del stations_data
        check_series_job(job_config)
    else:
        logger.verbose("[TODO]: Update JOBS")
        status = [JobConfig.Status.FAILED.value, JobConfig.Status.PENDING.value]
        filters = create_job_filters(job_config, status, last_check=False)
        count = count_job(job_config, filters)
        if count:
            logger.info(f"Initiating {count} jobs for {job_config}")
            trigger_job(job_config, filters)
        else:
            logger.info(f"No pending jobs for {job_config}.\n")


def create_series_jobs(stations_data: List[SerieStationData], job_config: JobConfig) -> None:
    """ Creates Series Jobs for each SerieStationData received for a given JobConfig.
    Preprocess all years from "Start Date" to "End Date" that will become a job request.
    """
    start = time.time()
    jobs = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_period, *data, job_config)
                   for data in stations_data]
        for future in as_completed(futures):
            try:
                processed_jobs = future.result()
                jobs.extend(processed_jobs)
            except Exception as e:
                logger.error(f"Error processing period: {e}")
    insert_jobs(jobs)
    elapsed = time.time() - start
    logger.info(f"Created {len(jobs)} jobs for {job_config} in {elapsed:.2f} seconds")


def process_period(station_code, start_date, end_date, job_config):
    jobs = []
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

    if start_date > end_date:
        logger.trace(f"Bigger start date {start_date} than end date {end_date} for station {station_code}")
        jobs.append(SeriesJobs(
            StationID  = station_code,
            FromDate   = start_date,
            ToDate     = end_date,
            Status     = JobConfig.Status.CORRUPTED.value,
            HidroTable = job_config
        ))
        return jobs
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
            Status     = JobConfig.Status.PENDING.value,
            HidroTable = job_config
        ))
        if next_year < end_date:
            current_year = next_year
        else:
            break
    return jobs


write_queue: Queue[QueueData] = Queue()
def trigger_job(job_config: JobConfig, filters) -> None:
    """ Triggers an Thread Worker for each pending or falied job entrie in DB for a given JobConfig."""

    writer = Thread(target=db_writer, daemon=True)
    writer.start()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(handle_job_request, job, job_config)
                   for job in get_jobs(job_config, filters)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"[WORKER]: {e}")

    finish_queue = QueueData(
        job_config  = job_config,
        job         = None,
        items       = None,
        worker_time = 0,
        stop_signal = True
    )
    write_queue.put(finish_queue)
    writer.join()
    status_map = {1: "Pending", 2: "Failed", 5: "Completed"}
    counts = {status_map.get(s, f"Unknown({s})"): c for s, c in count_job_by_status(job_config)}
    logger.info(f"Pending: {counts.get('Pending', 0)}, Failed: {counts.get('Failed', 0)}, Completed: {counts.get('Completed', 0)}\n")


token_lock = Lock()
def handle_job_request(job: HidroJob, job_config: JobConfig) -> None:
    """ Request data of an HidroJob.
    Validate data on success return, and convert to ORM model before writing on Queue.
    """

    start = time.time()
    with token_lock:
        token = get_token()
    success, items = request_job_data(job_config, token, job.to_params())

    if success:
        job.Status = JobConfig.Status.COMPLETED.value
        match job_config:
            case JobConfig.Base():
                job.LastCheck = datetime.now()
    else:
        job.Status = JobConfig.Status.FAILED.value
    elapsed = time.time() - start
    logger.verbose(f"[WORKER]: Job {job.ID} completed in {elapsed:.2f} seconds")
    queue_data = QueueData(
        job_config  = job_config,
        job         = job,
        items       = items,
        worker_time = elapsed,
        stop_signal = False
    )
    write_queue.put(queue_data)


def db_writer() -> None:
    """ Single Writer Thread running during an Job.
    Consumes an Queue writen by each worker and write data in batches.
    """

    batch_buffer = {"jobs": [], "data": []}
    total_data     = 0
    total_jobs     = 0

    worker_elapsed = 0
    total_elapsed  = 0
    insert_elapsed = 0
    batch_elapsed  = 0
    batch_start_time = None
    while True:
        try:
            job_config, job, data, worker_time, stop_signal = write_queue.get()
            worker_elapsed += worker_time
            if job:
                batch_buffer["jobs"].append(job)
            if data:
                batch_buffer["data"].extend(data)
                if batch_start_time is None:
                    batch_start_time = time.time()

            if len(batch_buffer["data"]) >= BATCH_SIZE or stop_signal:
                if batch_start_time is not None:
                    batch_elapsed = time.time() - batch_start_time
                total_data     += len(batch_buffer["data"])
                total_jobs     += len(batch_buffer["jobs"])
                insert_elapsed  = write_data(job_config,
                                             batch_buffer["jobs"],
                                             batch_buffer["data"])
                total_elapsed += batch_elapsed + insert_elapsed

                logger.verbose(f"""[TIMER {job_config}]: """
                               f"""Time to reach batch: {batch_elapsed}, """
                               f"""Time to insert batch: {insert_elapsed}. """)

                logger.info(f"""[WRITER {job_config}]: """
                            f"""Total processed Data: {total_data}, """
                            f"""Total finished Jobs: {total_jobs}. """)
                logger.trace(f"""[TIMER {job_config}]: """
                            f"""Total worker elapsed: {worker_elapsed}, """
                            f"""Total writer elapsed: {total_elapsed}.""")

                batch_buffer["jobs"].clear()
                batch_buffer["data"].clear()
                batch_start_time = None

            if stop_signal:
                logger.info(f"""[WRITER]: Finished jobs for {job_config} """
                            f"""Total processed Data: {total_data}, """
                            f"""Total finished Jobs: {total_jobs}.""")
                logger.info(f"""[WRITER]: Total worker elapsed: {worker_elapsed}, """
                            f"""Total writer elapsed: {total_elapsed}.""")
                break;

        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")
            raise

        finally:
            write_queue.task_done()


def write_data(job_config: JobConfig, jobs: List[HidroJob], items) -> float:
    """Insert data into DB and update the jobs as well. """

    start_time = time.perf_counter()
    entries = []
    if len(items) > 0:
        match job_config:
            case JobConfig.Series():
                items = validate_series_items(job_config, items)
        match job_config:
            case JobConfig.Base():
                if job_config == "Estado":
                    check_keys = {"Codigo": "codigouf"}
                else:
                    check_keys = {f"Codigo": f'codigo{job_config.lower()}'}
                entries = handle_batch_update(job_config, items, check_keys)
                if entries:
                    insert_hidro(entries)
            case (JobConfig.Series.RAIN      | JobConfig.Series.DISCHARGE_SUMMARY |
                  JobConfig.Series.FLOW_RATE | JobConfig.Series.SEDIMENTS         |
                  JobConfig.Series.STAGE):
                check_keys = {'EstacaoCodigo': 'codigoestacao', 'Data': 'Data_Hora_Dado'}
                entries = handle_batch_update(job_config, items, check_keys)
                if entries:
                    insert_hidro(entries)

            case JobConfig.Series.GRANULOMETRY:
                check_keys = {'EstacaoCodigo': 'codigoestacao', 'Data': 'Data_Dado',
                              'HoraInicial': 'Hora_Inicial', 'HoraFinal': 'Hora_Final'}
                entries = handle_batch_update(job_config, items, check_keys)
                if entries:
                    insert_hidro(entries)

            case JobConfig.Series.DISCHARGE_FLOW:
                check_keys = {'EstacaoCodigo': 'codigoestacao', 'NumeroCurva': 'Numero_Curva',
                              'PeriodoValidadeInicio': 'Periodo_Validade_Inicio',
                              'PeriodoValidadeFim': 'Periodo_Validade_Fim'}
                entries = handle_batch_update(job_config, items, check_keys)
                if entries:
                    insert_hidro(entries)

            case JobConfig.Series.WATER_QUALITY:
                check_keys = {'EstacaoCodigo': 'codigoestacao', 'Data': 'Data_Hora_Dado'}
                entries = handle_batch_update(job_config, items, check_keys)
                if entries:
                    entries = insert_hidro(entries, False)
                    entry_lookup = {}
                    for entry in entries:
                        key = (getattr(entry, 'EstacaoCodigo'), getattr(entry, 'Data'))
                        entry_lookup[key] = entry
                    for item in items:
                        key = (item['codigoestacao'], item['Data_Hora_Dado'])
                        if key in entry_lookup:
                            item['Registro_ID'] = entry_lookup[key].RegistroID
                    check_keys = {f'{job_config}ID': 'Registro_ID'}
                    water_status_entries = handle_batch_update(f'{job_config}Status', items, check_keys)
                    if water_status_entries:
                        insert_hidro(water_status_entries)
            case JobConfig.Series():
                entries = data_to_model_orm(job_config, items)
                has_id = True if job_config == JobConfig.Serial.CROSS_SECTION else False
                insert_hidro(entries, has_id)
    if len(jobs) > 0:
        update_jobs(jobs, job_config)
        logger.trace(f"[WRITER {job_config}]: Updated {len(jobs)} jobs")
    elapsed_time = time.perf_counter() - start_time
    if entries:
        logger.trace(f"[WRITER {job_config}]: Inserted {len(entries)} entries in {elapsed_time} seconds")
    return elapsed_time


def validate_series_items(job_config: JobConfig, items):
    """Validate returned data by the API. """

    match job_config:
        case JobConfig.Series.RAIN:
            dict_len = 76
        case JobConfig.Series.DISCHARGE_SUMMARY:
            dict_len = 10
        case JobConfig.Series.DISCHARGE_FLOW:
            dict_len = 18
        case JobConfig.Series.STAGE:
            dict_len = 78
        case JobConfig.Series.GRANULOMETRY:
            dict_len = 117
        case JobConfig.Series.CROSS_SECTION:
            dict_len = 18
        case JobConfig.Series.WATER_QUALITY:
            dict_len = 303
        case JobConfig.Series.SEDIMENTS:
            dict_len = 18
        case _:
            dict_len = None

    if dict_len:
        items = [item for item in items if len(item) == dict_len]

    seen = set()
    filtered = []
    for index, item in enumerate(items):
        try:
            match job_config:
                case (JobConfig.Series.RAIN      | JobConfig.Series.DISCHARGE_SUMMARY |
                      JobConfig.Series.STAGE     | JobConfig.Series.WATER_QUALITY     |
                      JobConfig.Series.SEDIMENTS | JobConfig.Series.FLOW_RATE):
                    key = (item['codigoestacao'], item['Data_Hora_Dado'])
                case JobConfig.Series.GRANULOMETRY:
                    key = (item['codigoestacao'], item['Data_Dado'],
                           item['Hora_Inicial'], item['Hora_Final'])
                case JobConfig.Series.DISCHARGE_FLOW:
                    key = (item['codigoestacao'], item['Numero_Curva'],
                           item['Periodo_Validade_Inicio'], item['Periodo_Validade_Fim'])

            if key not in seen:
                seen.add(key)
                filtered.append(item)
            else:
                logger.verbose(f"[VALIDATE JOB]: Duplicated item: {key}")

        except Exception as e:
            logger.error(f"Error at index {index}: {e}")
            logger.error(f"Item: {item}, type: {type(item)}")
            pass

    if filtered:
        items = filtered

    return items


def convert_json_items(job_config, items):
    for item in items:
        for key, value in item.items():
            if isinstance(value, str):
                try:
                    item[key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    match job_config:
                        case JobConfig.Series.GRANULOMETRY:
                            formats = ["%Y-%m-%d %H:%M:%S.%f",
                                       "%Y-%m-%d %H:%M:%S",
                                       "%Y-%m-%d", "%H:%M:%S"]
                            for fmt in formats:
                                try:
                                    item[key] = datetime.strptime(value, fmt)
                                    break
                                except Exception as e:
                                    continue
                        case _:
                            try:
                                item[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                            except ValueError:
                                pass
    return items


def run():
    for job in JobConfig.Base:
        check_base_job(job)
    for job in JobConfig.Series:
        check_series_job(job)
