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

import logging
logger = logging.getLogger(__name__)

from typing import List

from hidrodb.models.hidro  import *

HIDRO_DB = None

_HIDRO_MODELS_MAP = {
    "Bacia":                 Basin,
    "SubBacia":              SubBasin,
    "Entidade":              Entity,
    "Municipio":             Township,
    "Rio":                   River,
    "Estado":                State,
    "Estacao":               Station,
    "Chuvas":                Rain,
    "ResumoDescarga":        DischargeSummary,
    "CurvaDescarga":         DischargeFlow,
    "Sedimentos":            Sediments,
    "QualAgua":              WaterQuality,
    "QualAguaStatus":        WaterQualityStatus,
    "Cotas":                 Stage,
    "Granulometria":         Granulometry,
    "PerfilTransversal":     CrossSection,
    "PerfilTransversalVert": VerticalCrossSection,
    "Vazoes":                FlowRate,
}


def get_hidro_model(name: str):
    return _HIDRO_MODELS_MAP[name]


def insert_hidro(collection: List[HidroBase], expire = True) -> List[HidroBase]:
    """ Insert a list of Hidro ORM Model into Hidro Database"""

    hidro_session = HIDRO_DB.get_session()
    hidro_session.expire_on_commit = expire
    hidro_session.add_all(collection)
    hidro_session.flush()
    hidro_session.commit()
    hidro_session.close()
    return collection


def count_hidro(model: HidroBase):
    """ Counts a given Model in Hidro Database. """

    hidro_session = HIDRO_DB.get_session()
    count_model   = hidro_session.query(model).count()
    hidro_session.close()
    return count_model


def get_states() -> State:
    """ Returns registered States in Hidro Database. """

    hidro_session = HIDRO_DB.get_session()
    states = hidro_session.query(State).filter(State.CodigoIBGE.isnot(None)).all()
    hidro_session.close()
    return states


def get_period(model_name: str, only_code=False, with_null_end_date=False):
    """ Returns stations with initial and final periods for an given table in Hidro Database. """

    model = get_hidro_model(model_name)
    statement = model.create_period_statement(only_code, with_null_end_date)
    hidro_session = HIDRO_DB.get_session()
    period_data = hidro_session.execute(statement)
    hidro_session.close()
    return period_data


def handle_batch_update(job_name: str, items):

    hidro_session = HIDRO_DB.get_session()
    model = get_hidro_model(job_name)
    check_keys = get_verify_keys(job_name)

    filter_values = {}
    for model_key, json_key in check_keys.items():
        filter_values[model_key] = [item.get(json_key) for item in items]

    query = hidro_session.query(model)
    for model_key, values in filter_values.items():
        attr = getattr(model, model_key)
        query = query.filter(attr.in_(values))

    existing = query.all()

    existing_map = {}
    for e in existing:
        key = tuple(getattr(e, k) for k in check_keys.keys())
        existing_map[key] = e

    new_entries = []
    for item in items:
        key = tuple(item.get(check_keys[k]) for k in check_keys.keys())
        entry = existing_map.get(key)
        if entry:
            entry.from_json(item)
            from sqlalchemy import inspect
            if inspect(entry).modified:
                logger.info(f"Updated {model.__tablename__} entry code {key}.")
                hidro_session.merge(entry)
                hidro_session.commit()
            else:
                logger.verbose(f"No Updates for {model.__tablename__} entry code {key}.")
        else:
            new_entries.append(model.from_json(item))
            logger.verbose(f"New {model.__tablename__} entry code {key}.")
    hidro_session.close()
    return new_entries


def get_verify_keys(name: str):
    match name:
        case ("Bacia"     | "SubBacia" | "Entidade" |
              "Municipio" | "Rio"      | "Estacao"):
            return {"Codigo": f"codigo{name.lower()}"}
        case "Estado":
            return {"Codigo": "codigouf"}
        case ("Chuvas" | "ResumoDescarga" |
              "Vazoes" | "Sedimentos"     | "Cotas"):
            return {'EstacaoCodigo': 'codigoestacao',
                    'Data': 'Data_Hora_Dado'}
        case "Granulometria":
            return {'EstacaoCodigo': 'codigoestacao',
                    'Data': 'Data_Dado',
                    'HoraInicial': 'Hora_Inicial',
                    'HoraFinal': 'Hora_Final'}
        case "CurvaDescarga":
            return {'EstacaoCodigo': 'codigoestacao',
                    'NumeroCurva': 'Numero_Curva',
                    'PeriodoValidadeInicio': 'Periodo_Validade_Inicio',
                    'PeriodoValidadeFim': 'Periodo_Validade_Fim'}
        case "QualAgua":
            return {'EstacaoCodigo': 'codigoestacao',
                    'Data': 'Data_Hora_Dado'}

