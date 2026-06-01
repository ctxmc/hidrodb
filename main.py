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

import os
import argparse
import requests
import json
from datetime import datetime
from queue import Queue
from threading import Thread

from database import *
from hidro_webservices import *

def check_token(client):
    client.cursor.execute("SELECT COUNT(*) FROM Token")
    if (not client.cursor.fetchone()[0]):
        print("No Token present, requesting.")
        token, expires = request_token(client)
        client.cursor.execute("""INSERT INTO Token (Token, Expires)"""
                              f"""VALUES ('{token}', '{expires}');""")
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

def check_table(hidro, client, table):
    hidro.cursor.execute(f"SELECT COUNT(*) FROM {table}")
    if (not hidro.cursor.fetchone()[0]):
        print(f"{table} has no Entries, requesting data")
        if (check_token(client)):
            client.cursor.execute("SELECT Token FROM Token")
            token = client.cursor.fetchone()[0]
            match table:
                case "Bacia":
                    basins = request_basins(token)
                    insert_basins(hidro, basins, table)
                case "SubBacia":
                    sub_basins = request_sub_basins(token)
                    insert_sub_basins(hidro, sub_basins, table)
                case "Entidade":
                    entities = request_entity(token)
                    insert_entities(hidro, entities, table)
                case "Municipio":
                    towns = request_township(token)
                    insert_towns(hidro, towns, table)
                case "Rio":
                    rivers = request_rivers(token)
                    insert_rivers(hidro, rivers, table)
                case "Estado":
                    states = request_states(token)
                    insert_states(hidro, states, table)
                case "Estacao":
                    hidro.cursor.execute("SELECT Sigla FROM Estado WHERE CodigoIBGE IS NOT NULL")
                    for (UF,) in hidro.cursor.fetchall():
                        if (check_token(client)):
                            client.cursor.execute("SELECT Token FROM Token")
                            token       = client.cursor.fetchone()[0]
                            stations    = request_stations(token, UF)
                            if len(stations) > 0:
                                insert_stations(hidro, stations, table)
                case "Chuvas":
                    jobs = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
                    jobs.cursor.execute(f"SELECT COUNT(*) FROM RAIN")
                    jobs_count = jobs.cursor.fetchone()[0]
                    jobs.close()
                    if (not jobs_count):
                        print("Praparing Jobs for collection")
                        stations_with_rain_data_sql = (
                            "SELECT Codigo, "
                            "CASE  "
                            "WHEN PeriodoRegistradorChuvaInicio IS NOT NULL "
                            "AND PeriodoRegistradorChuvaFim IS NULL THEN 'active' "
                            "WHEN PeriodoRegistradorChuvaInicio IS NOT NULL "
                            "AND PeriodoRegistradorChuvaFim IS NOT NULL THEN 'finished' "
                            "END AS status "
                            "FROM Estacao "
                            "WHERE PeriodoRegistradorChuvaInicio IS NOT NULL "
                            "OR PeriodoRegistradorChuvaFim IS NOT NULL "
                        )
                        hidro.cursor.execute(stations_with_rain_data_sql)
                        active, finished = [], []
                        for code, status in hidro.cursor.fetchall():
                            (active if status.strip() == 'active' else finished).append(code)
                        print(
                            f"\nTotal stations with rain data: {len(active+finished)}"
                            f"\nTotal stations with finished rain data collection: {len(finished)}"
                            f"\nTotal stations with active rain data collection: {len(active)}"
                        )
                        prepare_rain_collection_job(hidro, (finished + active))
                        handle_rain_job()
                    else:
                        handle_rain_job()
                case _:
                    print(f"TODO {table}")
    else:
        print(f"{table} has Entries; TODO")

def prepare_rain_collection_job(hidro, stations_code):
    jobs = []
    for station_code in stations_code:
        station_data_sql = (
            "SELECT PeriodoRegistradorChuvaInicio, PeriodoRegistradorChuvaFim "
            "FROM Estacao WHERE Codigo = ?"
        )
        hidro.cursor.execute(station_data_sql, (station_code,))
        (start, end), = hidro.cursor.fetchall()
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        if end is None:
            end = datetime.today()
        else:
            end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        total_years = end.year - start.year
        current_year = start
        for count_year in range(1, total_years+1):
            next_year = current_year.replace(year=current_year.year+1)
            if next_year > end:
                next_year = end
            jobs.append((
                station_code,
                current_year.strftime("%Y-%m-%d %H:%M:%S"),
                next_year.strftime("%Y-%m-%d %H:%M:%S"),
                JobStatus.PENDING.value
            ))
            current_year = next_year
    insert_jobs(jobs, "Rain")

def handle_rain_job():
    print("Initiating jobs for collect rain data")
    job_queue = Queue()
    rain_collection = Queue()
    threads = [Thread(target=worker, args=(job_queue, rain_collection), daemon=True) for _ in range(10)]
    for t in threads:
        t.start()
    db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    db.cursor.execute(
        "SELECT ID, StationID, FromDate, ToDate FROM Rain "
        f"WHERE Status = {JobStatus.PENDING.value} "
        f"OR Status = {JobStatus.FAILED.value}"
    )
    for job_id, station_code, from_date, to_date in db.cursor.fetchall():
        job_queue.put((job_id, station_code, from_date, to_date))
    job_queue.join()
    results = []
    while not rain_collection.empty():
        results.append(rain_collection.get())
    print(results)

def worker(job_queue, rain_collection):
    while True:
        task = job_queue.get()
        if task is None:
            break
        handle_rain(*task, rain_collection)
        job_queue.task_done()

def handle_rain(job_id, station_code, current_year, next_year, rain_collection):
    client = DatabaseConnection("client.mdb", DatabaseType.CLIENT)
    if (check_token(client)):
        client.cursor.execute("SELECT Token FROM Token")
        token = client.cursor.fetchone()[0]
        rain_data = request_rain_data(token, station_code, current_year, next_year)
        if len(rain_data) > 0:
            print(f"Got rain data for station {station_code} on period ({current_year})-({next_year})")
            rain_collection.put(rain_data)
        else:
            print(f"Rain data for station {station_code} on period ({current_year})-({next_year}) is null")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hidro',  type=str, default='hidro.mdb')
    parser.add_argument('--client', type=str, default='client.mdb')
    parser.add_argument('--jobs',   type=str, default='jobs.mdb')
    args = parser.parse_args()

    create_db(args.client)
    client = DatabaseConnection(args.client, DatabaseType.CLIENT)
    init_db(client)

    create_db(args.hidro)
    hidro = DatabaseConnection(args.hidro, DatabaseType.HIDRO)
    init_db(hidro)

    create_db(args.jobs)
    jobs = DatabaseConnection(args.jobs, DatabaseType.JOBS)
    init_db(jobs)
    jobs.close()

    tables = [
        "Bacia", "SubBacia", "Entidade",
        "Municipio", "Rio", "Estado",
        "Estacao", "Chuvas"
    ]
    for table in tables:
        check_table(hidro, client, table)

    client.close()
    hidro.close()

if __name__ == "__main__":
    main()
