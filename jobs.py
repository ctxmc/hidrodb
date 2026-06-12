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

from datetime import datetime, timedelta

from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Thread, Lock
import time
from enum import Enum, auto

from database import *
from hidro_webservices import *

class JobStatus(Enum):
    PENDING   = auto()
    FAILED    = auto()
    INVALID   = auto()
    CORRUPTED = auto()
    COMPLETED = auto()

def check_token(client):
    client.cursor.execute("SELECT COUNT(*) FROM Token")
    if (not client.cursor.fetchone()[0]):
        print("No Token present, requesting.")
        token, expires = request_token(client)
        insert_token = "INSERT INTO Token (Token, Expires) VALUES (?, ?)"
        client.cursor.execute(insert_token, (token, expires))
        return True
    else:
        client.cursor.execute("SELECT Expires FROM Token")
        expires_ISOND = client.cursor.fetchone()[0]
        expires_datetime = datetime.strptime(expires_ISOND, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expires_datetime:
            return True
        else:
            print("Token expired, requesting new.")
            token, expires = request_token(client)
            client.cursor.execute("""UPDATE [Token] SET"""
                                  f"""[Token]   = '{token}',"""
                                  f"""[Expires] = '{expires}'"""
                                  f"""WHERE [Expires] = '{expires_ISOND}';""")
            print("Token updated.")
            return True

def check_job(job_name):
    print(f"\nChecking Job for {job_name}")
    jobs_db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    jobs_db.cursor.execute(f"SELECT COUNT(*) FROM {job_name}")
    jobs_count = jobs_db.cursor.fetchone()[0]
    if (not jobs_count):
        print(f"Creating jobs for {job_name}")
        match job_name:
            case "Chuvas":
                sql = (
                    "SELECT Codigo, PeriodoRegistradorChuvaInicio, PeriodoRegistradorChuvaFim "
                    "FROM Estacao WHERE PeriodoRegistradorChuvaInicio IS NOT NULL"
                )
            case "ResumoDescarga" | "CurvaDescarga":
                sql = (
                    "SELECT Codigo, PeriodoDescLiquidaInicio, PeriodoDescLiquidaFim "
                    "FROM Estacao WHERE PeriodoDescLiquidaInicio IS NOT NULL"
                )
            case "Sedimentos":
                sql = (
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case "QualAgua":
                sql = (
                    "SELECT Codigo, PeriodoQualAguaInicio, PeriodoQualAguaFim "
                    "FROM Estacao WHERE PeriodoQualAguaInicio IS NOT NULL"
                )
            case "Cotas":
                sql = ("""
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
                sql = (
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case "PerfilTransversal":
                sql = (
                    "SELECT Codigo, PeriodoSedimentosInicio, PeriodoSedimentosFim "
                    "FROM Estacao WHERE PeriodoSedimentosInicio IS NOT NULL"
                )
            case _:
                print(f"TODO: {job_name}")
                return
        hidro = DatabaseConnection("hidro.mdb", DatabaseType.HIDRO)
        hidro.cursor.execute(sql)
        stations_data = hidro.cursor.fetchall()
        hidro.close()
        create_jobs(stations_data, job_name)
        jobs_db.close()
        check_job(job_name)
    else:
        print("TODO: Update JOBS?")
        jobs_db.cursor.execute(
            "SELECT ID, StationID, FromDate, ToDate "
            f"FROM {job_name} WHERE Status = {JobStatus.FAILED.value} "
            f"OR                    Status = {JobStatus.PENDING.value}"
        )
        jobs = jobs_db.cursor.fetchall()
        if (len(jobs) > 1):
            trigger_job(jobs, job_name)
        else:
            print(f"No pending jobs for {job_name}")

def create_jobs(stations_data, table):
    jobs = []
    for station_code, start_date, end_date in stations_data:
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if end_date is None:
            end_date = datetime.today() - timedelta(days=1)
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        if start_date > datetime.today():
            jobs.append((
                station_code,
                start_date.strftime("%Y-%m-%d %H:%M:%S"),
                end_date.strftime("%Y-%m-%d %H:%M:%S"),
                JobStatus.CORRUPTED.value
            ))
        total_years  = end_date.year - start_date.year
        current_year = start_date
        for count_year in range(1, total_years+1):
            next_year = current_year.replace(year=current_year.year+1)
            if next_year > end_date:
                next_year = end_date
            jobs.append((
                station_code,
                current_year.strftime("%Y-%m-%d %H:%M:%S"),
                next_year.strftime("%Y-%m-%d %H:%M:%S"),
                JobStatus.PENDING.value
            ))
            current_year = next_year
    insert_jobs(jobs, table)
    print(f"Created {len(jobs)} jobs for Table {table}")

write_queue = Queue()
def trigger_job(jobs, job_name):
    print(f"Initiating jobs for {job_name}")
    writer = Thread(target=db_writer, daemon=True)
    writer.start()
    MAX_WORKERS=1
    client_db = DatabaseConnection("client.mdb", DatabaseType.CLIENT)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for job in jobs:
            executor.submit(handle_job, job, job_name, client_db)
        executor.shutdown(wait=True)
    client_db.close()
    write_queue.put((job_name, None, None, None, True))
    writer.join()

lock = Lock()
def handle_job(job_data, job_name, client_db):
    job_id, station_code, initial_date, final_date = job_data
    with lock:
        check_token(client_db)
        client_db.cursor.execute("SELECT Token FROM Token")
        token = client_db.cursor.fetchone()[0]
    match job_name:
        case "Chuvas":
            status, data = request_serial_data(token, HidroEndpoint.RAIN,
                                                station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 76):
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [Rain(entrie) for entrie in data]
            else:
                status = JobStatus.FAILED
        case "ResumoDescarga":
            status, data = request_serial_data(token, HidroEndpoint.DISCHARGE_SUMMARY,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 10):
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [DischargeSummary(entrie) for entrie in data]
            else:
                status = JobStatus.FAILED
        case "Sedimentos":
            status, data = request_serial_data(token, HidroEndpoint.SEDIMENTS,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                data = [Sediments(item) for item in data]
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
                data = [Stage(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "CurvaDescarga":
            status, data = request_serial_data(token, HidroEndpoint.DISCHARGE_FLOW,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                for entrie in data:
                    if (len(entrie) != 18):
                        status = JobStatus.INVALID
                        break
                if status == JobStatus.COMPLETED:
                    data = [DischargeFlow(item) for item in data]
            else:
                status = JobStatus.FAILED
        case "Granulometria":
            status, data = request_serial_data(token, HidroEndpoint.GRANULOMETRY,
                                               station_code, initial_date, final_date)
            if status:
                status = JobStatus.COMPLETED
                data = [Granulometry(item) for item in data]
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
    print(f"""\n[JOB {job_name} {job_id}]: {status_label} request for station {station_code} """
          f"""on period ({initial_date})-({final_date})""")
    write_queue.put((job_name, job_id, status.value, data, False))

def db_writer():
    hidro_db = DatabaseConnection("hidro.mdb", DatabaseType.HIDRO)
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
                print(f"""Total Data: {total_data}, """
                      f"""Total Jobs: {total_jobs}, """
                      f"""Total thread elapsed: {total_elapsed}""")
                print(f"Finished jobs for {job_name}")
                break;
            batch_buffer["jobs"].append((status, job_id))
            if len(data) > 0:
                batch_buffer["data"].extend(data)
            if len(batch_buffer["data"]) >= BATCH_SIZE:
                total_data    += len(batch_buffer["data"])
                total_jobs    += len(batch_buffer["jobs"])
                total_elapsed += write_data(hidro_db, job_name,
                                            batch_buffer["jobs"], batch_buffer["data"])
                print(f"""[WRITER {job_name}]: Total Data: {total_data}, """
                      f"""Total Jobs: {total_jobs}, """
                      f"""Total thread elapsed: {total_elapsed}""")
                batch_buffer = {"jobs": [], "data": []}
        except Exception as e:
            print(f"[WRITER ERROR]: db_writer exception: {e}")

def write_data(hidro_db, job_name, job_data, hidro_data):
    start_time = time.perf_counter()
    if len(hidro_data) > 0:
        match job_name:
            case "Chuvas":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "ResumoDescarga":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "Sedimentos":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "Cotas":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "CurvaDescarga":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "Granulometria":
                insert_hidro(hidro_db, job_name, hidro_data)
            case "QualAgua":
                water_quality = [WaterQuality(item) for item in hidro_data]
                insert_hidro(hidro_db, job_name, water_quality)
                water_status  = [WaterQualityStatus(item) for item in hidro_data]
                insert_hidro(hidro_db, f"{job_name}Status", water_status)
            case "PerfilTransversal":
                cross_section   = []
                v_cross_section = []
                current_id      = None
                for data in hidro_data:
                    data_id = data.get("Registro_ID")
                    if current_id == data_id:
                        continue
                    current_id = data_id
                    cross_section.append(CrossSection(data))
                    import re, ast;
                    verticals_str = re.sub(r'(\w+)=', r'"\1":', data.get("verticais"))
                    verticals     = ast.literal_eval(verticals_str)
                    v_cross_section.extend([VerticalCrossSection(v, current_id) for v in verticals])
                insert_hidro(hidro_db, job_name, cross_section, True)
                insert_hidro(hidro_db, f"{job_name}Vert", v_cross_section, True)
    if len(job_data) > 0:
        update_jobs(job_name, job_data)
        print(f"[WRITER {job_name}]: Updated {len(job_data)} jobs")
    elapsed_time = time.perf_counter() - start_time
    print(f"[WRITER {job_name}]: Inserted {len(hidro_data)} entries in {elapsed_time} seconds")
    return elapsed_time
