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
from datetime import datetime, timedelta

from database import *
from hidro_webservices import *
from jobs import *

def check_table(hidro, client, table):
    hidro.cursor.execute(f"SELECT COUNT(*) FROM {table}")
    if (not hidro.cursor.fetchone()[0]):
        print(f"\n{table} has no Entries, requesting data")
        if (check_token(client)):
            client.cursor.execute("SELECT Token FROM Token")
            token = client.cursor.fetchone()[0]
            match table:
                case "Bacia":
                    data = [Basin(item) for item in request_basins(token)]
                    insert_hidro(hidro, table, data)
                case "SubBacia":
                    data = [SubBasin(item) for item in request_sub_basins(token)]
                    insert_hidro(hidro, table, data)
                case "Entidade":
                    data = [Entity(item) for item in request_entity(token)]
                    insert_hidro(hidro, table, data)
                case "Municipio":
                    data = [Township(item) for item in request_township(token)]
                    insert_hidro(hidro, table, data)
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
                case _:
                    print(f"TODO: {table}")
    else:
        print(f"{table} has Entries; TODO")

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
        "Estacao"
    ]
    for table in tables:
        check_table(hidro, client, table)

    jobs = [
        "Chuvas", "ResumoDescarga",
        "Sedimentos", "QualAgua",
        "Cotas", "CurvaDescarga"
    ]
    for job in jobs:
        check_job(job)

    client.close()
    hidro.close()

if __name__ == "__main__":
    main()
