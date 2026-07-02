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
from queue              import Queue
from threading          import Thread, Lock

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

    class Serial(StrEnum):
        """ Enum to hold Hidro Jobs that will run with threads. """

        STATION           = "Estacao"
        RAIN              = "Chuvas"
        DISCHARGE_SUMMARY = "ResumoDescarga"
        DISCHARGE_FLOW    = "CurvaDescarga"
        SEDIMENTS         = "Sedimentos"
        WATER_QUALITY     = "QualAgua"
        STAGE             = "Cotas"
        GRANULOMETRY      = "Granulometria"
        CROSS_SECTION     = "PerfilTransversal"
        FLOW_RATE         = "Vazoes"


class JobStatus(Enum):
    """ Enum to control job status."""

    PENDING   = auto()
    """Job is queued and waiting to be processed."""

    FAILED    = auto()
    """Job request failed."""

    INVALID   = auto()
    """Job request returned item had incorrect fields."""

    CORRUPTED = auto()
    """Job with incorrect start date."""

    COMPLETED = auto()
    """Job successfully completed."""

    def get_label(self) -> str:
        """ :returns: a string label for each status."""
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


def check_base_job(job: JobConfig.Base) -> None:
    """Checks each HidroJob and request/update them.

    :param job: Current Job to check, insert and update.
    :returns: Nothing.
    """

    model    = get_hidro_model(job)
    logger.verbose(f"Checking {job}.")
    if not count_hidro(model):
        logger.info(f"{job} has no Entries, requesting data.")
        token = get_token()
        if (token):
            success, items = request_job_data(job, token, {})
            entries = [model.from_json(item) for item in items]
            insert_hidro(entries)
    else:
        logger.info(f"Checking updates for {job}.")


def check_stations_jobs() -> None:
    """Checks if there is Stations entries on database.
    Request all national stations by UF if there isnt.
    """
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
        count = count_job(JobConfig.Serial.STATION, status)
        if count:
            logger.info(f"Initiating {count} jobs for {JobConfig.Serial.STATION}")
            trigger_job(JobConfig.Serial.STATION)
        else:
            logger.info(f"No pending jobs for Stations")


def check_series_job(job_config: JobConfig) -> None:
    """Checks an JobConfig.
    Create jobs if there is no entries and start pending jobs requisition.
    """

    logger.trace(f"Checking Job for {job_config}")
    if not count_job(job_config):
        logger.info(f"Creating jobs for {job_config}")
        match job_config:
            case JobConfig.Serial.RAIN:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_rain_period()]
            case (JobConfig.Serial.DISCHARGE_SUMMARY
                  | JobConfig.Serial.DISCHARGE_FLOW
                  | JobConfig.Serial.CROSS_SECTION
                  | JobConfig.Serial.FLOW_RATE
            ):
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_discharge_period()]
            case JobConfig.Serial.SEDIMENTS | JobConfig.GRANULOMETRY:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_sediments_period()]
            case JobConfig.Serial.WATER_QUALITY:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_water_period()]
            case JobConfig.Serial.STAGE:
                stations_data = [SerieStationData(code, start, end)
                                 for code, start, end in get_stage_period()]
        create_series_jobs(stations_data, job_config)
        del stations_data
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
    """ Creates Series Jobs for each SerieStationData received for a given JobConfig.
    Preprocess all years from "Start Date" to "End Date" that will become a job request.
    """
    start = time.time()
    jobs = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_period, *data, job_config)
                   for data in stations_data]
        for future in as_completed(futures):
            jobs.extend(future.result())
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
    if start_date > datetime.today():
        logger.warning(f"Corrupted start date {start_date} for station {station_code}")
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
        current_year = next_year
    return jobs


write_queue: Queue[QueueData] = Queue()
def trigger_job(job_config: JobConfig) -> None:
    """ Triggers an Thread Worker for each pending or falied job entrie in DB for a given JobConfig."""

    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        status = [JobStatus.FAILED.value, JobStatus.PENDING.value]
        for index, job in enumerate(get_jobs_yield(job_config, status)):
            executor.submit(handle_job_request, job, job_config)
    finish_queue = QueueData(
        job_config  = job_config,
        job         = None,
        items       = None,
        stop_signal = True
    )
    write_queue.put(finish_queue)
    writer.join()


token_lock = Lock()
def handle_job_request(job: HidroJob, job_config: JobConfig) -> None:
    """ Request data of an HidroJob.
    Validate data on success return, and convert to ORM model before writing on Queue.
    """


    with token_lock:
        token = get_token()
    success, items = request_job_data(job_config, token, job.to_params())

    if success:
        match job_config:
            case JobConfig.Serial.STATION:
                job.Status    = JobStatus.COMPLETED
                job.LastCheck = datetime.now()
            case _:
                job, items = validate_data(job_config, items, job)
    else:
        job.Status = JobStatus.FAILED

    if job.Status == JobStatus.COMPLETED and len(items) > 0:
        data = data_to_model_orm(job_config, items)
    else:
        data = []

    if isinstance(job, SeriesJobs):
        logger.verbose(f"""[JOB {job_config} {job.ID}]: {job.Status.get_label()} """
                       f"""request for station {job.StationID} """
                       f"""on period ({job.FromDate})-({job.ToDate})""")

    queue_data = QueueData(
        job_config  = job_config,
        job         = job,
        items       = items,
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

    total_elapsed  = 0
    insert_elapsed = 0
    batch_start_time = None
    while True:
        job_config, job, data, stop_signal = write_queue.get()
        try:
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
                total_elapsed  += batch_elapsed + insert_elapsed

                logger.info(f"""[WRITER {job_config}]: """
                            f"""Total processed Data: {total_data}, """
                            f"""Total finished Jobs: {total_jobs}. """)
                logger.trace(f"""[TIMER {job_config}]: """
                            f"""Time to reach batch: {batch_elapsed}, """
                            f"""Time to insert batch: {insert_elapsed}. """)
                logger.trace(f"""[TIMER {job_config}]: """
                            f"""Total writer elapsed: {total_elapsed}.""")

                batch_buffer["jobs"].clear()
                batch_buffer["data"].clear()
                batch_start_time = None


            if stop_signal:
                logger.info(f"""Finished jobs for {job_config}""")
                break;

        except Exception as e:
            logger.error(f"[WRITER]: db_writer exception: {e}")
            raise

        finally:
            write_queue.task_done()


def write_data(job_config: JobConfig, jobs: List[HidroJob], items) -> float:
    """Insert data into DB and update the jobs as well. """

    start_time = time.perf_counter()
    if len(items) > 0:
        has_id = True if job_config == JobConfig.Serial.CROSS_SECTION else False
        insert_hidro(hidro_data, has_id)
    if len(jobs) > 0:
        update_jobs(jobs, job_config)
        logger.trace(f"[WRITER {job_config}]: Updated {len(jobs)} jobs")
    elapsed_time = time.perf_counter() - start_time
    logger.trace(f"[WRITER {job_config}]: Inserted {len(items)} entries in {elapsed_time} seconds")
    return elapsed_time


def validate_data(job_config: JobConfig, items: dict, job: HidroJob) -> (HidroJob, dict):
    """Validate returned data by the API. """

    #TODO: VALIDATE EACH JSON KEY FOR EACH TABLE?
    job.Status = JobStatus.COMPLETED

    match job_config:
        case JobConfig.Serial.RAIN:
            dict_len = 76
        case JobConfig.Serial.DISCHARGE_SUMMARY:
            dict_len = 10
        case JobConfig.Serial.DISCHARGE_FLOW:
            dict_len = 18
        case JobConfig.Serial.STAGE:
            dict_len = 78
        case JobConfig.Serial.GRANULOMETRY:
            dict_len = 117
        case JobConfig.Serial.CROSS_SECTION:
            dict_len = 18
        case JobConfig.Serial.WATER_QUALITY:
            dict_len = 303
        case _:
            #TODO: CHECK LEN FOR EVERY TABLE?
            return (job, items)

    for item in items:
        if (len(item) != dict_len):
            items   = []
            job.Status = JobStatus.INVALID
            logger.verbose(f"[VALIDATE JOB {job.ID}] Invalid item: {item}")
            break

    return (job, items)



