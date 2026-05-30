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

import jaydebeapi
import jpype
import msaccessdb
import os
from enum import StrEnum
import getpass
from datetime import datetime

jpype.startJVM()
jpype.addClassPath('./UCanAccess-5.0.1.bin/ucanaccess-5.0.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-lang3-3.8.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-logging-1.2.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/hsqldb-2.5.0.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/jackcess-3.0.1.jar')

class DatabaseType(StrEnum):
    HIDRO  = "Hidro"
    CLIENT = "Client"

class DatabaseConnection:
    def __init__(self, dbq: str, db_type: DatabaseType):
        self.connection = jaydebeapi.connect(
            'net.ucanaccess.jdbc.UcanaccessDriver',
            f'jdbc:ucanaccess://{dbq}',
            ['', '']
        )
        self.cursor = self.connection.cursor()
        self.type   = db_type

    def close(self):
        self.cursor.close()
        self.connection.close()

def create_db(db_path):
    if not os.path.isfile(db_path):
        print(f"Error: {db_path} does not exists")
        print(f"Creating {db_path}")
        msaccessdb.create(db_path)
    else:
        print(f"{db_path} exists.")

def init_db(db):
    meta   = db.connection.jconn.getMetaData()
    tables = meta.getTables(None, None, None, ["TABLE"])
    if not tables.next():
        print(f"No tables found for {db.type} Database. Initializing.")
        match db.type:
            case DatabaseType.HIDRO:
                execute_sql_file(db, "hidro.sql")
                VERSION = '1.4.0.000'
                db.cursor.execute(f"INSERT INTO Versao (Versao) VALUES ('{VERSION}');")
                print(f"Initialized {db.type} Database Version {VERSION}.")
            case DatabaseType.CLIENT:
                execute_sql_file(db, "client.sql")
                user_id  = input("Enter API username: ")
                password = getpass.getpass("Enter API password: ")
                db.cursor.execute("""INSERT INTO Credentials (ID, Password)"""
                                   f"""VALUES ('{user_id}', '{password}');""")
                print(f"Initialized {db.type} Database.")
    else:
        print(f"{db.type} Database is Initialized.")

def execute_sql_file(db, sql_file_path):
    if not os.path.isfile(sql_file_path):
        print(f"Error: {sql_file_path} does not exists")
        return
    with open(sql_file_path, "r") as f:
        sql_script = f.read()
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
    for stmt in statements:
        db.connection.jconn.createStatement().execute(stmt)

def insert_basins(hidro, basins, table):
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

def insert_sub_basins(hidro, sub_basins, table):
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

def insert_entities(hidro, entities, table):
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

def insert_towns(hidro, towns, table):
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

def insert_rivers(hidro, rivers, table):
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

def insert_states(hidro, states, table):
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
