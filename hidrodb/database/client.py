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

from sqlalchemy     import func
from sqlalchemy.sql import elements

from typing import List

from hidrodb.models.client import *

CLIENT_DB   = None

def count_client(model: ClientBase):
    """ Counts a given Model in Client Database. """

    client_session = CLIENT_DB.get_session()
    count_model    = client_session.query(model).count()
    client_session.close()
    return count_model


def insert_credentials(user_id, password):
    """ Insert an Credentials model entrie in Client Database. """

    credentials = Credentials(ID=user_id, Password=password)
    client_session = CLIENT_DB.get_session()
    client_session.add(credentials)
    client_session.commit()
    client_session.close()


def check_credentials():
    return count_client(Credentials)


def get_credentials() -> Credentials:
    """ Gets the first registered Credential on Client Database and returns it. """

    client_session = CLIENT_DB.get_session()
    credentials    = client_session.query(Credentials).first()
    client_session.close()
    return credentials


def get_token_model() -> Token:
    """ Returns the first found Token on Client Database """

    client_session = CLIENT_DB.get_session()
    token          = client_session.query(Token).first()
    client_session.close()
    return token


def add_token(client_id, token, expires):
    """ Add an Token to Client Database """

    client_session = CLIENT_DB.get_session()
    client_session.add(Token(CredentialID=client_id, Token=token, Expires=expires))
    client_session.commit()
    client_session.close()


def update_token(RegistroID, new_token, new_expires):
    """ Updates an Token on Client Database """

    client_session = CLIENT_DB.get_session()
    from sqlalchemy import update;
    update_expression = (
        update(Token).where(Token.RegistroID == RegistroID)
        .values(Token=new_token, Expires=new_expires)
    )
    client_session.execute(update_expression)
    client_session.commit()
    client_session.close()


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


def create_job_filters(job_name: str, status: List[int], last_check: bool, stations=[]) -> List[elements]:

    model   = get_job_model(job_name)
    filters = [model.HidroTable == job_name]
    if stations:
        filters.append(model.StationID.in_(stations))
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

    
def count_job(job_name: str, filters: List[elements]) -> int:
    """ Counts jobs registered in Client Database. """

    client_session = CLIENT_DB.get_session()
    model          = get_job_model(job_name)
    count_job      = client_session.query(model).filter(*filters).count()
    client_session.close()
    return count_job


def count_job_by_status(job_name: str):

    client_session = CLIENT_DB.get_session()
    model          = get_job_model(job_name)
    count_jobs     = (client_session.query(model.Status, func.count(model.ID).label('count'))
                      .filter(model.HidroTable == job_name, model.Status != 4)
                      .group_by(model.Status).order_by(model.Status).all())
    client_session.close()
    return count_jobs


def get_jobs(job_name: str, filters: List[elements]):
    """ Returns all Series Jobs on Client Database, yield then in batches """

    client_session = CLIENT_DB.get_session()
    model          = get_job_model(job_name)
    jobs = client_session.query(model).filter(*filters).all()
    client_session.close()
    return jobs


def insert_jobs(jobs: List[HidroJob]) -> None:
    """ Insert a list of Jobs into Client Database. """

    client_session = CLIENT_DB.get_session()
    client_session.add_all(jobs)
    client_session.commit()
    client_session.close()


def update_jobs(jobs: List[HidroJob], job_name: str) -> None:
    """ Updates a list of Jobs. """

    client_session = CLIENT_DB.get_session()
    client_session.bulk_update_mappings(get_job_model(job_name), jobs)
    client_session.commit()
    client_session.close()

def get_lesser_year(job_name: str, station_ids):
    client_session = CLIENT_DB.get_session()
    lesser_results = client_session.query(SeriesJobs).filter(
        SeriesJobs.HidroTable == job_name,
        SeriesJobs.StationID.in_(station_ids),
        SeriesJobs.Status != 4,
        (func.julianday(SeriesJobs.ToDate) - func.julianday(SeriesJobs.FromDate)) < 365
    ).distinct().all()
    client_session.close()
    return lesser_results
