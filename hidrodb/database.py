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

from sqlalchemy     import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session

from enum   import StrEnum
from typing import List

from models.hidro  import *
from models.client import *
from config        import *

class DatabaseType(StrEnum):
    HIDRO  = "Hidro"
    CLIENT = "Client"

class DatabaseConnection:
    def __init__(self, dbq: str, db_type: DatabaseType):
        self.engine  = create_engine(f"sqlite:///{dbq}", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.type    = db_type
    def get_session(self) -> Session:
        return self.Session()
    def close(self):
        self.engine.dispose()

def init_db(db: DatabaseConnection) -> None:
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
                ClientBase.metadata.create_all(db.engine)
                user_id = input("Enter API username: ")
                import getpass
                password = getpass.getpass("Enter API password: ")
                credentials = Credentials(ID=user_id, Password=password)
                session.add(credentials)
                session.commit()
        session.commit()

def execute_sql_file(db: DatabaseConnection, sql_file_path: str, parameters=None) -> None:
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
        
def insert_hidro(collection: List[HidroBase], has_id=False) -> None:
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    if not has_id:
        model_class = type(collection[0])
        reg_id  = (hidro_session.query(func.max(model_class.RegistroID)).scalar() or 0) + 1
        for i, entry in enumerate(collection):
            entry.RegistroID = reg_id + i
    else:
        import warnings;
        from sqlalchemy import exc as sa_exc;
        warnings.filterwarnings('ignore', '.*Identity map already had an identity.*', sa_exc.SAWarning)
    hidro_session.add_all(collection)
    hidro_session.commit()
    hidro_session.close()
    hidro_db.close()

def insert_jobs(jobs: List[HidroJob]) -> None:
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.add_all(jobs)
    client_session.commit()
    client_session.close()
    client_db.close()

def update_jobs(jobs: List[HidroJob], job_config: JobConfig) -> None:
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.bulk_update_mappings(job_config.get_job_model(), jobs)
    client_session.commit()
    client_session.close()
    client_db.close()

def count_client(model: ClientBase):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    count_model    = client_session.query(model).count()
    client_session.close()
    client_db.close()
    return count_model

def get_credentials() -> Credentials:
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    credentials    = client_session.query(Credentials).first()
    client_session.close()
    client_db.close()
    return credentials

def add_token(client_id, token, expires):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.add(Token(CredentialID=client_id, Token=token, Expires=expires))
    client_session.commit()
    client_session.close()
    client_db.close()

def get_token_model() -> Token:
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    token          = client_session.query(Token).first()
    client_session.close()
    client_db.close()
    return token

def update_token(RegistroID, new_token, new_expires):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    from sqlalchemy import update;
    update_expression = (
        update(Token).where(Token.RegistroID == RegistroID)
        .values(Token=new_token, Expires=new_expires)
    )
    client_session.execute(update_expression)
    client_session.commit()
    client_session.close()
    client_db.close()

def get_station_jobs(status) -> StationJobs:
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    station_jobs   = client_session.query(StationJobs).filter(StationJobs.Status.in_(status)).all()
    client_session.close()
    client_db.close()
    return station_jobs

def get_series_jobs(job_config, status):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    series_jobs = (client_session.query(SeriesJobs).filter(
        SeriesJobs.Status.in_(status), SeriesJobs.HidroTable == job_config).all())
    client_session.close()
    client_db.close()
    return series_jobs

def get_jobs_yield(job_config, status):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    model = job_config.get_job_model()
    try:
        query = (client_session.query(model).filter(
            model.Status.in_(status),
            model.HidroTable == job_config))
        for job in query.yield_per(100):
            yield job
    finally:
        client_session.close()
        client_db.close()

def count_job(job_config: JobConfig, status = None):
    client_db      = DatabaseConnection(client_path, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    model          = job_config.get_job_model()
    filters        = [model.HidroTable == job_config]
    if status:
        filters.append(model.Status.in_(status))
    count_job = client_session.query(model).filter(*filters).count()
    client_session.close()
    client_db.close()
    return count_job

def count_hidro(model: HidroBase):
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    count_model   = hidro_session.query(model).count()
    hidro_session.close()
    hidro_db.close()
    return count_model

def get_states() -> State:
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    states = hidro_session.query(State).filter(State.CodigoIBGE.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return states

def get_rain_period():
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    rain_period = hidro_session.query(
        Station.Codigo,
        Station.PeriodoRegistradorChuvaInicio,
        Station.PeriodoRegistradorChuvaFim
    ).filter(Station.PeriodoRegistradorChuvaInicio.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return rain_period

def get_discharge_period():
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    discharge_period = hidro_session.query(
        Station.Codigo,
        Station.PeriodoDescLiquidaInicio,
        Station.PeriodoDescLiquidaFim
    ).filter(Station.PeriodoDescLiquidaInicio.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return discharge_period

def get_sediments_period():
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    sediments_period = hidro_session.query(
        Station.Codigo,
        Station.PeriodoSedimentosInicio,
        Station.PeriodoSedimentosFim
    ).filter(Station.PeriodoSedimentosInicio.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return sediments_period

def get_water_period():
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    water_period = hidro_session.query(
        Station.Codigo,
        Station.PeriodoQualAguaInicio,
        Station.PeriodoQualAguaFim
    ).filter(Station.PeriodoQualAguaInicio.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return water_period

def get_stage_period():
    hidro_db      = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    sql = text("""
    SELECT 
        Codigo, 
        MIN(PeriodoInicio) AS PeriodoInicio, 
        MIN(PeriodoFim)    AS PeriodoFim
    FROM (
        SELECT Codigo, PeriodoEscalaInicio AS PeriodoInicio, PeriodoEscalaFim AS PeriodoFim
        FROM Estacao WHERE PeriodoEscalaInicio IS NOT NULL
        UNION
        SELECT Codigo, PeriodoRegistradorNivelInicio, PeriodoRegistradorNivelFim
        FROM Estacao WHERE PeriodoRegistradorNivelInicio IS NOT NULL
    ) combined
    GROUP BY Codigo;
    """)
    stage_period = hidro_session.execute(sql).fetchall()
    hidro_session.close()
    hidro_db.close()
    return stage_period
