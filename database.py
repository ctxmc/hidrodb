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
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session

from enum import StrEnum
from datetime import datetime

from models.hidro_models import *

class DatabaseType(StrEnum):
    HIDRO  = "Hidro"
    CLIENT = "Client"
    JOBS   = "Jobs"

class DatabaseConnection:
    def __init__(self, dbq: str, db_type: DatabaseType):
        self.engine  = create_engine(f"sqlite:///{dbq}", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.type    = db_type
    def get_session(self) -> Session:
        return self.Session()
    def close(self):
        self.engine.dispose()

def init_db(db):
    session = db.get_session()
    check_tables_sql = text("SELECT name FROM sqlite_master WHERE type='table'")
    result = session.execute(check_tables_sql)
    tables = result.fetchall()
    if not tables:
        logger.info(f"No tables found for {db.type} Database. Initializing.")
        match db.type:
            case DatabaseType.HIDRO:
                execute_sql_file(db, "tables/hidro.sql")
                VERSION = '1.4.0.000'
                session.execute(text(f"INSERT INTO Versao (Versao) VALUES ('{VERSION}')"))
                logger.info(f"Initialized {db.type} Database Version {VERSION}.")
            case DatabaseType.CLIENT:
                execute_sql_file(db, "tables/client.sql")
                user_id = input("Enter API username: ")
                import getpass
                password = getpass.getpass("Enter API password: ")
                insert_user_sql = f"INSERT INTO Credentials (ID, Password) VALUES ('{user_id}', '{password}')"
                session.execute(text(insert_user_sql))
                logger.info(f"Initialized {db.type} Database.")
            case DatabaseType.JOBS:
                execute_sql_file(db, "tables/jobs.sql")
                logger.info(f"Initialized {db.type} Database.")
        session.commit()

def execute_sql_file(db, sql_file_path, parameters=None):
    if not os.path.isfile(sql_file_path):
        logger.error(f"{sql_file_path} does not exist")
        return
    with open(sql_file_path, "r") as f:
        sql_script = f.read()
    with db.engine.connect() as conn:
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for stmt in statements:
            if parameters and '?' in stmt:
                conn.exec_driver_sql(stmt, parameters)
            else:
                conn.exec_driver_sql(stmt)
        conn.commit()
        
def insert_hidro(hidro, collection, has_id=False):
    session = hidro.get_session()
    if not has_id:
        model_class = type(collection[0])
        reg_id  = (session.query(func.max(model_class.RegistroID)).scalar() or 0) + 1
        for i, entry in enumerate(collection):
            entry.RegistroID = reg_id + i
    session.add_all(collection)
    session.commit()

def insert_jobs(jobs, sql):
    db = DatabaseConnection(jobs_path, DatabaseType.JOBS)
    session = db.get_session()
    session.execute(sql, jobs)
    session.commit()
    db.close()

def update_jobs(table, jobs):
    db = DatabaseConnection(jobs_path, DatabaseType.JOBS)
    session = db.get_session()
    session.execute(text(f"UPDATE [{table}] SET [Status] = :status WHERE [ID] = :job_id"), jobs)
    session.commit()
    db.close()
