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
import requests
import json
import time

from datetime import datetime
from enum     import StrEnum

import logging
logger = logging.getLogger(__name__)

class HidroEndpoint(StrEnum):
    AUTH              = "/EstacoesTelemetricas/OAUth/v1"
    BASIN             = "/EstacoesTelemetricas/HidroBacia/v1"
    SUB_BASIN         = "/EstacoesTelemetricas/HidroSubBacia/v1"
    ENTITY            = "/EstacoesTelemetricas/HidroEntidade/v1"
    TOWNSHIP          = "/EstacoesTelemetricas/HidroMunicipio/v1"
    RIVER             = "/EstacoesTelemetricas/HidroRio/v1"
    STATE             = "/EstacoesTelemetricas/HidroUF/v1"
    STATION           = "/EstacoesTelemetricas/HidroInventarioEstacoes/v1"
    RAIN              = "/EstacoesTelemetricas/HidroSerieChuva/v1"
    DISCHARGE_SUMMARY = "/EstacoesTelemetricas/HidroSerieResumoDescarga/v1"
    SEDIMENTS         = "/EstacoesTelemetricas/HidroSerieSedimentos/v1"
    STAGE             = "/EstacoesTelemetricas/HidroSerieCotas/v1"
    DISCHARGE_FLOW    = "/EstacoesTelemetricas/HidroSerieCurvaDescarga/v1"
    WATER_QUALITY     = "/EstacoesTelemetricas/HidroSerieQA/v1"
    GRANULOMETRY      = "/EstacoesTelemetricas/HidroSerieGranulometria/v1"
    CROSS_SECTION     = "/EstacoesTelemetricas/HidroSeriePerfilTransversal/v1"

def request_hidro_ws(endpoint, headers, params={}):
    url      = "https://www.ana.gov.br/hidrowebservice"
    response = requests.get(f"{url}{endpoint}", headers=headers, params=params)
    if response.ok:
        try:
            return response.json()
        except Exception as e:
            logger.error(f"(exception): {e}")
    else:
        logger.debug(f"Endpoint: {endpoint}\nHeaders: {headers}\nParams: {params}")
        try:
            logger.error(f"(json): {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            logger.error(f"(response): {response} (status: {response.status_code})")
        match response.status_code:
            case 503 | 504:
                time.sleep(1)

def request_token(client_id, client_password, max_retries=3, retry_delay=2):
    headers = {
        "accept":        "*/*",
        "Identificador": f"{client_id}",
        "Senha":         f"{client_password}",
    }
    for attempt in range(max_retries):
        try:
            data = request_hidro_ws(HidroEndpoint.AUTH, headers, {})
            token           = data.get("items", {}).get("tokenautenticacao")
            expires_RFC2822 = data.get("items", {}).get("validade")
            expires_ISOND   = datetime.strptime(expires_RFC2822, "%a %b %d %H:%M:%S GMT-03:00 %Y")
            return [token, expires_ISOND]
        except Exception as e:
            logger.error(f"(attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    raise

def request_data(token, endpoint, params=None):
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        file_path = get_file_path(endpoint, params)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                items = json.load(f)
        else:
            items = request_hidro_ws(endpoint, headers, params).get("items", {})
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        return items
    except Exception as e:
            logger.error(f"(exception): {e}")
            return []

def request_serial_data(token, endpoint, station_code, initial_date, final_date):
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    ymd_start = initial_date.strftime('%Y-%m-%d')
    ymd_end   = final_date.strftime('%Y-%m-%d')
    params    = {
        "Código da Estação": station_code,
        "Tipo Filtro Data": "DATA_LEITURA", # "DATA_ULTIMA_ATUALIZACAO"
        "Data Inicial (yyyy-MM-dd)": f"{ymd_start}",
        "Data Final (yyyy-MM-dd)": f"{ymd_end}"
    }
    try:
        dir_path  = get_dir_path(endpoint)
        file_path = f"./json/{dir_path}/station_{station_code}_{ymd_start}_{ymd_end}.json"
        items = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                items = json.load(f)
        else:
            items = request_hidro_ws(endpoint, headers, params).get("items", {})
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        return (True, items)
    except Exception as e:
            logger.error(f"(exception): {e}")
            return (False, [])

def get_file_path(endpoint, params):
    match endpoint:
        case HidroEndpoint.BASIN:
            return "./json/Bacia.json"
        case HidroEndpoint.SUB_BASIN:
            return "./json/SubBacia.json"
        case HidroEndpoint.ENTITY:
            return "./json/Entidade.json"
        case HidroEndpoint.TOWNSHIP:
            return "./json/Municipio.json"
        case HidroEndpoint.RIVER:
            return "./json/Rio.json"
        case HidroEndpoint.STATE:
            return "./json/Estado.json"
        case HidroEndpoint.STATION:
            UF = params["Unidade Federativa"]
            return f"./json/stations/Estacao_{UF}.json"

def get_dir_path(endpoint):
    match endpoint:
        case HidroEndpoint.RAIN:
            return "rain"
        case HidroEndpoint.DISCHARGE_SUMMARY:
            return "liquid_desc"
        case HidroEndpoint.SEDIMENTS:
            return "sediments"
        case HidroEndpoint.STAGE:
            return "stage"
        case HidroEndpoint.DISCHARGE_FLOW:
            return "discharge"
        case HidroEndpoint.WATER_QUALITY:
            return "qa"
        case HidroEndpoint.GRANULOMETRY:
            return "granulometry"
        case HidroEndpoint.CROSS_SECTION:
            return "profile"
