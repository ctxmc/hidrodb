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
Provides request functionalities to ANA HidroWebservices API
"""

import os, requests, json, time, logging
logger = logging.getLogger(__name__)

from datetime import datetime
from enum     import StrEnum

_DATA_ENDPOINTS_MAP = {
    "Bacia":             "/EstacoesTelemetricas/HidroBacia/v1",
    "SubBacia":          "/EstacoesTelemetricas/HidroSubBacia/v1",
    "Entidade":          "/EstacoesTelemetricas/HidroEntidade/v1",
    "Municipio":         "/EstacoesTelemetricas/HidroMunicipio/v1",
    "Rio":               "/EstacoesTelemetricas/HidroRio/v1",
    "Estado":            "/EstacoesTelemetricas/HidroUF/v1",
    "Estacao":           "/EstacoesTelemetricas/HidroInventarioEstacoes/v1",
    "Chuvas":            "/EstacoesTelemetricas/HidroSerieChuva/v1",
    "ResumoDescarga":    "/EstacoesTelemetricas/HidroSerieResumoDescarga/v1",
    "CurvaDescarga":     "/EstacoesTelemetricas/HidroSerieSedimentos/v1",
    "Sedimentos":        "/EstacoesTelemetricas/HidroSerieCotas/v1",
    "QualAgua":          "/EstacoesTelemetricas/HidroSerieCurvaDescarga/v1",
    "Cotas":             "/EstacoesTelemetricas/HidroSerieQA/v1",
    "Granulometria":     "/EstacoesTelemetricas/HidroSerieGranulometria/v1",
    "PerfilTransversal": "/EstacoesTelemetricas/HidroSeriePerfilTransversal/v1",
    "Vazoes":            "/EstacoesTelemetricas/HidroSerieVazao/v1"
}

def request_hidro_ws(endpoint, headers, params={}):
    """ Make a request to ANA API and returns the json."""

    url = "https://www.ana.gov.br/hidrowebservice"
    logger.trace(f"[REQUEST]: Endpoint: {endpoint}\nHeaders: {headers}\nParams: {params}")
    response = requests.get(f"{url}{endpoint}", headers=headers, params=params)
    if response.ok:
        try:
            return response.json()
        except Exception as e:
            logger.error(f"[REQUEST]: (exception): {e}")
    else:
        try:
            logger.error(f"[REQUEST]: (json): {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            logger.debug(f"[REQUEST]: (response): {response} (status: {response.status_code})")
        match response.status_code:
            case 401 | 503 | 504:
                time.sleep(1)
                return

def request_token(client_id: str, client_password: str, max_retries=3, retry_delay=2):
    """ Request an token to ANA API and returns it."""

    headers = {
        "accept":        "*/*",
        "Identificador": f"{client_id}",
        "Senha":         f"{client_password}",
    }
    endpoint = "/EstacoesTelemetricas/OAUth/v1"
    for attempt in range(max_retries):
        try:
            data = request_hidro_ws(endpoint, headers, {})
            token           = data.get("items", {}).get("tokenautenticacao")
            expires_RFC2822 = data.get("items", {}).get("validade")
            expires_ISOND   = datetime.strptime(expires_RFC2822, "%a %b %d %H:%M:%S GMT-03:00 %Y")
            return [token, expires_ISOND]
        except Exception as e:
            logger.warning(f"[TOKEN]: (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    raise Exception(f"Failed after {max_retries} attempts")


def request_job_data(job_name: str, token: str, params: dict) -> (bool, dict):
    """ Request data to ANA API and returns it."""

    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    endpoint = _DATA_ENDPOINTS_MAP[job_name]
    try:
        file_path = _get_file_path(job_name, params)
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
            logger.verbose(f"[REQUEST_DATA]: (exception): {e}")
            return (False, [])


def _get_file_path(job_name: str, params: dict) -> str:
    """ Returns file path to save returned json. """

    match job_name:
        case ("Bacia"     | "SubBacia" | "Entidade" |
              "Municipio" | "Rio"      | "Estado"):
            return f"./json/{job_name}.json"
        case "Estacao":
            UF = params["Unidade Federativa"]
            return f"./json/{job_name}/{job_name}_{UF}.json"
        case ("Chuvas"        | "ResumoDescarga"    | "CurvaDescarga" |
              "Sedimentos"    | "QualAgua"          | "Cotas"         |
              "Granulometria" | "PerfilTransversal" | "Vazoes"):
            station_code, _, ymd_start, ymd_end = params.values()
            return f"./json/{job_name}/station_{station_code}_{ymd_start}_{ymd_end}.json"
