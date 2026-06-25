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
Provides database connection and SQL queries throught ORM.
"""

import logging
logger = logging.getLogger(__name__)

from sqlalchemy     import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session

from enum   import StrEnum
from typing import List

from hidrodb.models.hidro  import *
from hidrodb.models.client import *
from hidrodb.config        import *

class DatabaseType(StrEnum):
    """
    Enum to name databases
    """

    HIDRO  = "Hidro"
    CLIENT = "Client"

class DatabaseConnection:
    """ Class to hold database engine."""

    def __init__(self, dbq: str, db_type: DatabaseType):
        self.engine  = create_engine(f"sqlite:///{dbq}", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.type    = db_type

    def get_session(self) -> Session:
        return self.Session()
    def close(self):
        self.engine.dispose()


def init_db(db_path, db_type) -> None:
    """ Init an DatabaseConnection, if there is no tables, creates then"""

    db = DatabaseConnection(db_path, db_type)
    session = db.get_session()
    check_tables_sql = text("SELECT name FROM sqlite_master WHERE type='table'")
    result = session.execute(check_tables_sql)
    tables = result.fetchall()
    if not tables:
        logger.info(f"No tables found for {db.type} Database. Initializing.")
        match db.type:
            case DatabaseType.HIDRO:
                HidroBase.metadata.create_all(db.engine)
            case DatabaseType.CLIENT:
                ClientBase.metadata.create_all(db.engine)
        session.commit()
    session.close()
    db.close()


def insert_credentials(user_id, password):
    """ Insert an Credentials model entrie in Client Database. """

    credentials = Credentials(ID=user_id, Password=password)
    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.add(credentials)
    client_session.commit()
    client_session.close()
    client_db.close()


def insert_hidro(collection: List[HidroBase], has_id=False) -> None:
    """ Insert a list of Hidro ORM Model into Hidro Database"""

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
    """ Insert a list of Jobs into Client Database. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.add_all(jobs)
    client_session.commit()
    client_session.close()
    client_db.close()


def update_jobs(jobs: List[HidroJob], job_config: JobConfig) -> None:
    """ Updates a list of Jobs. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.bulk_update_mappings(job_config.get_job_model(), jobs)
    client_session.commit()
    client_session.close()
    client_db.close()


def count_client(model: ClientBase):
    """ Counts a given Model in Client Database. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    count_model    = client_session.query(model).count()
    client_session.close()
    client_db.close()
    return count_model


def get_credentials() -> Credentials:
    """ Gets the first registered Credential on Client Database and returns it. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    credentials    = client_session.query(Credentials).first()
    client_session.close()
    client_db.close()
    return credentials


def add_token(client_id, token, expires):
    """ Add an Token to Client Database """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.add(Token(CredentialID=client_id, Token=token, Expires=expires))
    client_session.commit()
    client_session.close()
    client_db.close()


def get_token_model() -> Token:
    """ Returns the first found Token on Client Database """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    token          = client_session.query(Token).first()
    client_session.close()
    client_db.close()
    return token


def update_token(RegistroID, new_token, new_expires):
    """ Updates an Token on Client Database """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
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
    """ Returns all Stations Jobs on Client Database """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    station_jobs   = client_session.query(StationJobs).filter(StationJobs.Status.in_(status)).all()
    client_session.close()
    client_db.close()
    return station_jobs


def get_jobs_yield(job_config, status):
    """ Returns all Series Jobs on Client Database, yield then in batches """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
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
    """ Counts jobs registered in Client Database. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
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
    """ Counts a given Model in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    count_model   = hidro_session.query(model).count()
    hidro_session.close()
    hidro_db.close()
    return count_model


def get_states() -> State:
    """ Returns registered States in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
    hidro_session = hidro_db.get_session()
    states = hidro_session.query(State).filter(State.CodigoIBGE.isnot(None)).all()
    hidro_session.close()
    hidro_db.close()
    return states


def get_rain_period():
    """ Returns Stations with Rain Periods in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
    """ Returns Stations with Discharge Periods in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
    """ Returns Stations with Sediments Periods in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
    """ Returns Stations with Water Periods in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
    """ Returns Stations with Stage Periods in Hidro Database. """

    hidro_db      = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
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
