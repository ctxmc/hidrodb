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

from hidro_models import *

jpype.startJVM()
jpype.addClassPath('./UCanAccess-5.0.1.bin/ucanaccess-5.0.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-lang3-3.8.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-logging-1.2.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/hsqldb-2.5.0.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/jackcess-3.0.1.jar')

class DatabaseType(StrEnum):
    HIDRO  = "Hidro"
    CLIENT = "Client"
    JOBS   = "Jobs"


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
                execute_sql_file(db, "tables/hidro.sql")
                VERSION = '1.4.0.000'
                db.cursor.execute(f"INSERT INTO Versao (Versao) VALUES ('{VERSION}');")
                print(f"Initialized {db.type} Database Version {VERSION}.")
            case DatabaseType.CLIENT:
                execute_sql_file(db, "tables/client.sql")
                user_id  = input("Enter API username: ")
                password = getpass.getpass("Enter API password: ")
                db.cursor.execute("""INSERT INTO Credentials (ID, Password)"""
                                   f"""VALUES ('{user_id}', '{password}');""")
                print(f"Initialized {db.type} Database.")
            case DatabaseType.JOBS:
                execute_sql_file(db, "tables/jobs.sql")
                print(f"Initialized {db.type} Database.")
    else:
        print(f"{db.type} Database is Initialized.")

def execute_sql_file(db, sql_file_path, parameters=None):
    if not os.path.isfile(sql_file_path):
        print(f"Error: {sql_file_path} does not exists")
        return
    with open(sql_file_path, "r") as f:
        sql_script = f.read()
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
    for stmt in statements:
        db.cursor.execute(stmt, parameters)

def insert_hidro(hidro, table, collection, with_id=False):
    if not with_id:
        hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
        reg_id = hidro.cursor.fetchone()[0]
        reg_id = 1 if reg_id is None else int(reg_id)
        entries = [AccessEntrie(reg_id+i, **data.fields) for i, data in enumerate(collection)]
    else:
        entries = [AccessEntrie.with_id(**data.fields) for data in collection]
    data = [entry.data() for entry in entries]
    insert_sql = f"INSERT INTO {table} ({entries[0].keys()}) VALUES ({entries[0].values()})"
    hidro.cursor.executemany(insert_sql, data)

def insert_jobs(jobs, table):
    db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    db.cursor.executemany(f"INSERT INTO {table} (StationID, FromDate, ToDate, Status) VALUES (?, ?, ?, ?)", jobs)
    db.close()

def update_jobs(table, jobs):
    db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    db.cursor.executemany(f"UPDATE [{table}] SET [Status] = ? WHERE [ID] = ?", jobs)
    db.close()
