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
                    stations_with_rain_data_sql = (
                        "SELECT Codigo, "
                        "CASE  "
                        "WHEN PeriodoRegistradorChuvaInicio IS NOT NULL AND PeriodoRegistradorChuvaFim IS NULL THEN 'active' "
                        "WHEN PeriodoRegistradorChuvaInicio IS NOT NULL AND PeriodoRegistradorChuvaFim IS NOT NULL THEN 'finished' "
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
                    print("\nColleting Stations with finished data:")
                    handle_rain_data(hidro, client, finished, table)
                    print("\nColleting Stations with active data:")
                    handle_rain_data(hidro, client, active, table)
                case _:
                    print(f"TODO {table}")
    else:
        print(f"{table} has Entries; TODO")

def insert_rain_data(hidro, client, stations_code):
    for station_code in stations_code:
        data = ""
        station_data_sql = (
            "SELECT e.Nome, e.TipoEstacao, e.estadoCodigo, e.municipioCodigo, "
            "e.PeriodoRegistradorChuvaInicio, e.PeriodoRegistradorChuvaFim, "
            "m.Nome as municipioNome, est.Sigla as Sigla "
            "FROM Estacao e "
            "LEFT JOIN Municipio m ON e.municipioCodigo = m.Codigo "
            "LEFT JOIN Estado est ON e.estadoCodigo = est.Codigo "
            "WHERE e.Codigo = ?"
        )
        hidro.cursor.execute(station_data_sql, (station_code,))
        (station_name, station_type, _, _, start, end, town_name, UF), = hidro.cursor.fetchall()
        start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        if end is None:
            end = datetime.today()
        else:
            end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        total_years = end.year - start.year
        print(
            f"""\nStation code: {station_code}"""
            f"""\nname: {station_name}"""
            f"""\ntype: {"Fluviométrica" if station_type == 1 else "Pluviometrica" }"""
            f"""\ntown: {town_name}, state: {UF}"""
            f"""\nstart: {start}"""
            f"""\nend: {end}"""
            f"""\nTotal: {total_years} years"""
        )
        current_year = start
        for count_year in range(1, total_years+1):
            next_year = current_year.replace(year=current_year.year+1)
            if next_year > end:
                next_year = end
            if (check_token(client)):
                print("TODO: Request Data")
                print("TODO: Insert Data")
            current_year = next_year

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hidro',  type=str, default='hidro.mdb')
    parser.add_argument('--client', type=str, default='client.mdb')
    args = parser.parse_args()

    create_db(args.client)
    client = DatabaseConnection(args.client, DatabaseType.CLIENT)
    init_db(client)

    create_db(args.hidro)
    hidro = DatabaseConnection(args.hidro, DatabaseType.HIDRO)
    init_db(hidro)

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
