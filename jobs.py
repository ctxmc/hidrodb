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

from typing import Optional
_token_cache: Optional[Token] = None
def get_token() -> str:
    """Authenticate and return access token.
    Returns: Valid token for requesition
    """
    global _token_cache
    logger.verbose("Cheking Token.")

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


def check_resource(resource: HidroResource) -> None:
    model    = resource.get_model()
    endpoint = resource.get_endpoint()
    logger.verbose(f"Checking {resource}.")
    if not count_hidro(model):
        logger.info(f"{resource} has no Entries, requesting data.")
        token = get_token()
        if (token):
            success, items = request_data(token, endpoint, {})
            entries = [model.from_json(item) for item in items]
            insert_hidro(entries)
    else:
        logger.info(f"Checking updates for {resource}.")

        
def check_stations_jobs() -> None:
    if not count_client(StationJobs):
        logger.info(f"Creating jobs for Stations.")
        stations_jobs = []
        for state in get_states():
            station_job = StationJobs(
                HidroTable = "Estacao",
                Status     = JobStatus.PENDING.value,
                UF         = state.Sigla
            )
            stations_jobs.append(station_job)
        insert_jobs(stations_jobs)
        check_stations_jobs()
    else:
        logger.trace(f"Stations has jobs.")
        status = [JobStatus.FAILED.value, JobStatus.PENDING.value]
        count = count_job(JobConfig.STATION, status)
        if count:
            logger.info(f"Initiating {count} jobs for {JobConfig.STATION}")
            trigger_job(JobConfig.STATION)
        else:
            logger.info(f"No pending jobs for Stations")


def check_series_job(job_config: JobConfig) -> None:
    logger.trace(f"Checking Job for {job_config}")
    if not count_job(job_config):
        logger.info(f"Creating jobs for {job_config}")
        match job_config:
            case JobConfig.RAIN:
                db_data = get_rain_period()
            case JobConfig.DISCHARGE_SUMMARY | JobConfig.DISCHARGE_FLOW | JobConfig.CROSS_SECTION:
                db_data = get_discharge_period()
            case JobConfig.SEDIMENTS | JobConfig.GRANULOMETRY:
                db_data = get_sediments_period()
            case JobConfig.WATER_QUALITY:
                db_data = get_water_period()
            case JobConfig.STAGE:
                db_data = get_stage_period()
        stations_data = [SerieStationData(code, start, end) for code, start, end in db_data]
        create_series_jobs(stations_data, job_config)
        check_series_job(job_config)
    else:
        logger.verbose("[TODO]: Update JOBS")
        status = [JobStatus.FAILED.value, JobStatus.PENDING.value]
        count = count_job(job_config, status)
        if count:
            logger.info(f"Initiating {count} jobs for {job_config}")
            trigger_job(job_config)
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
def trigger_job(job_config: JobConfig) -> None:
    global queue_data_size
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        status = [JobStatus.FAILED.value, JobStatus.PENDING.value]
        for index, job in enumerate(get_jobs_yield(job_config, status)):
            executor.submit(handle_job, job, job_config)
    write_queue.put((job_config, None, None, True))
    writer.join()


lock = Lock()
def handle_job(job: HidroJob, job_config: JobConfig) -> None:
    with lock:
        token = get_token()
    success, data = request_data(token, job_config.get_endpoint(), job.to_params())

    if success:
        match job_config:
            case JobConfig.STATION:
                job.Status    = JobStatus.COMPLETED
                job.LastCheck = datetime.now()
            case _:
                job, data = validate_data(job_config, data, job)
    else:
        job.Status = JobStatus.FAILED

    if isinstance(job, SeriesJobs):
        logger.trace(f"""[JOB {job_config} {job.ID}]: {job.Status.get_label()} """
                     f"""request for station {job.StationID} """
                     f"""on period ({job.FromDate})-({job.ToDate})""")
    write_queue.put((job_config, job, data, False))


def db_writer() -> None:
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
                total_elapsed += write_data(job_config, batch_buffer["jobs"], batch_buffer["data"])
                logger.info(f"""[WRITER {job_config}]: Total Data: {total_data}, """
                            f"""Total Jobs: {total_jobs}, """
                            f"""Total thread elapsed: {total_elapsed}""")
                batch_buffer["jobs"].clear()
                batch_buffer["data"].clear()

            if stop_signal:
                logger.info(f"""Finished jobs for {job_config}""")
                break;

        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")
            raise

def write_data(job_config: JobConfig, jobs: List[HidroJob], hidro_data: dict) -> float:
    start_time = time.perf_counter()
    if len(hidro_data) > 0:
        logger.trace(f"[WRITER {job_config}]: Inserting {len(hidro_data)} entries")
        model_data = data_to_model_orm(job_config, hidro_data)
        has_id = True if job_config == JobConfig.CROSS_SECTION else False
        insert_hidro(model_data, has_id)
    if len(jobs) > 0:
        update_jobs(jobs, job_config)
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
                    model_data.append(job_config.get_hidro_model().from_json(item))
                model_data.append(VerticalCrossSection.from_json(item, current_id))
        case _:
            for data in hidro_data:
                model_data.append(job_config.get_hidro_model().from_json(data))
    return model_data
