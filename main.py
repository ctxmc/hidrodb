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
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, code, name in basins:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # TODO: USING datetime.min because this executemany dont allow NULL or "" for DateTime
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        items.append((reg_id, 0, 0, 0, 0, code, name, time, last_date))
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                    Codigo, Nome, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case "SubBacia":
                    sub_basins = request_sub_basins(token)
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, code, code_basin, name in sub_basins:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        items.append((reg_id, 0, 0, 0, 0, code, code_basin, name, time, last_date))
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                    BaciaCodigo, Codigo, Nome, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case "Entidade":
                    entities = request_entity(token)
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, code, name, acronym in entities:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        items.append(
                            (reg_id, 0, 0, 0, 0,
                             code, name, acronym,
                             time, last_date)
                        )
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                        Codigo, Nome, Sigla, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case "Municipio":
                    towns = request_township(token)
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, state_code, IBGE_code, name, code in towns:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        # TODO: USING -1 this executemany dont allow NULL or "" for Long
                        IBGE_code = -1 if IBGE_code is None else IBGE_code
                        items.append(
                            (reg_id, 0, 0, 0, 0,
                             state_code, code, IBGE_code,
                             name, time, last_date)
                        )
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                    EstadoCodigo, Codigo, CodigoIBGE, Nome, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case "Rio":
                    rivers = request_rivers(token)
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, code, basin_code, sub_basin_code, name, jurisdiction in rivers:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        # TODO: USING 0 this executemany dont allow NULL or "" for Byte
                        jurisdiction = 0 if jurisdiction is None else jurisdiction
                        items.append(
                            (reg_id, 0, 0, 0, 0,
                             basin_code, sub_basin_code,
                             code, name, jurisdiction,
                             time, last_date)
                        )
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                    BaciaCodigo, SubBaciaCodigo, Codigo, Nome, Jurisdicao, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case "Estado":
                    states = request_states(token)
                    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
                    reg_id = hidro.cursor.fetchone()[0]
                    reg_id = 1 if reg_id is None else int(reg_id)
                    items = []
                    for last_date, code, IBGE_code, acronym, name in states:
                        time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        last_date = datetime.min.strftime("%Y-%m-%d %H:%M:%S") if last_date is None else last_date
                        IBGE_code = -1 if IBGE_code is None else IBGE_code
                        items.append(
                            (reg_id, 0, 0, 0, 0,
                             code, IBGE_code, acronym,
                             name, time, last_date)
                        )
                        reg_id += 1
                    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
                    Codigo, CodigoIBGE, Sigla, Nome, DataIns, DataAlt"""
                    values = ','.join('?' for _ in cols.split(','))
                    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)
                    return
                case _:
                    print(f"TODO {table}")
                    return
    else:
        print(f"{table} has Entries; TODO")

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

    check_table(hidro, client, "Bacia")
    check_table(hidro, client, "SubBacia")
    check_table(hidro, client, "Entidade")
    check_table(hidro, client, "Municipio")
    check_table(hidro, client, "Rio")
    check_table(hidro, client, "Estado")

    client.close()
    hidro.close()

if __name__ == "__main__":
    main()
