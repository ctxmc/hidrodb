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
from sqlalchemy.sql import elements

from enum   import StrEnum
from typing import List

from hidrodb.models.hidro  import *
from hidrodb.models.client import *

CLIENT_PATH = None
HIDRO_PATH  = None

_HIDRO_MODELS_MAP = {
    "Bacia":             Basin,
    "SubBacia":          SubBasin,
    "Entidade":          Entity,
    "Municipio":         Township,
    "Rio":               River,
    "Estado":            State,
    "Estacao":           Station,
    "Chuvas":            Rain,
    "ResumoDescarga":    DischargeSummary,
    "CurvaDescarga":     DischargeFlow,
    "Sedimentos":        Sediments,
    "QualAgua":          WaterQuality,
    "Cotas":             Stage,
    "Granulometria":     Granulometry,
    "PerfilTransversal": CrossSection,
    "Vazoes":            FlowRate,
}

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


def update_jobs(jobs: List[HidroJob], job_name: str) -> None:
    """ Updates a list of Jobs. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    client_session.bulk_update_mappings(get_job_model(job_name), jobs)
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


def create_job_filters(job_name: str, status: List[int], last_check: bool) -> List[elements]:
    model   = get_job_model(job_name)
    filters = [model.HidroTable == job_name]
    if status or last_check:
        sub_filters = []
        if status:
            sub_filters.append(model.Status.in_(status))
        if last_check:
            from datetime import date
            sub_filters.append(model.LastCheck < date.today())
        if sub_filters:
            from sqlalchemy import or_
            filters.append(or_(*sub_filters))
    return filters


def get_jobs(job_name: str, filters: List[elements]):
    """ Returns all Series Jobs on Client Database, yield then in batches """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    model          = get_job_model(job_name)
    jobs = client_session.query(model).filter(*filters).all()
    client_session.close()
    client_db.close()
    return jobs


def count_job(job_name: str, filters: List[elements]) -> int:
    """ Counts jobs registered in Client Database. """

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    model          = get_job_model(job_name)
    count_job      = client_session.query(model).filter(*filters).count()
    client_session.close()
    client_db.close()
    return count_job

def count_job_by_status(job_name: str):

    client_db      = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    client_session = client_db.get_session()
    model          = get_job_model(job_name)
    count_jobs     = (client_session.query(model.Status, func.count(model.ID).label('count'))
                      .filter(model.HidroTable == job_name, model.Status != 4)
                      .group_by(model.Status).order_by(model.Status).all())
    client_session.close()
    client_db.close()
    return count_jobs


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

def get_hidro_model(name: str):
    return _HIDRO_MODELS_MAP[name]

def get_job_model(name: str):
    match name:
        case ("Bacia"     | "SubBacia" | "Entidade" |
              "Municipio" | "Rio"      | "Estado"):
            return BaseJobs
        case "Estacao":
            return StationJobs
        case ("Chuvas"        | "ResumoDescarga"    | "CurvaDescarga" |
              "Sedimentos"    | "QualAgua"          | "Cotas"         |
              "Granulometria" | "PerfilTransversal" | "Vazoes"):
            return SeriesJobs


def check_credentials():
    return count_client(Credentials)


def data_to_model_orm(job_config: str, items: dict):
    """Convert returned data by the API into the correspondent ORM Model of the job. """

    model_data = []
    match job_config:
        case "QualAgua":
            for item in items:
                model_data.append(WaterQuality.from_json(item))
                model_data.append(WaterQualityStatus.from_json(item))
        case "PerfilTransversal":
            current_id      = None
            for item in items:
                item_id = item.get("Registro_ID")
                if current_id != item_id:
                    current_id = item_id
                    model_data.append(get_hidro_model(job_config).from_json(item))
                model_data.append(VerticalCrossSection.from_json(item, current_id))
        case _:
            for item in items:
                model_data.append(get_hidro_model(job_config).from_json(item))
    return model_data
