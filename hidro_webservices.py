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

import requests
import json
from datetime import datetime

from database import *

def request_hidro_ws(endpoint, headers, params):
    url      = "https://www.ana.gov.br/hidrowebservice"
    response = requests.get(f"{url}{endpoint}", headers=headers, params=params)
    if response.ok:
        try:
            return response.json()
        except Exception as e:
            print(f"Error (exception): {e}")
    else:
        try:
            print(f"Error (json): {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Error (response): {response}")

def request_token(client):
    client.cursor.execute("SELECT ID FROM Credentials")
    client_id = client.cursor.fetchone()[0]
    client.cursor.execute("SELECT Password FROM Credentials")
    client_password = client.cursor.fetchone()[0]
    endpoint = "/EstacoesTelemetricas/OAUth/v1"
    headers = {
        "accept":        "*/*",
        "Identificador": f"{client_id}",
        "Senha":         f"{client_password}",
    }
    data = request_hidro_ws(endpoint, headers, {})
    token           = data.get("items", {}).get("tokenautenticacao")
    expires_RFC2822 = data.get("items", {}).get("validade")
    expires_ISOND   = datetime.strptime(expires_RFC2822, "%a %b %d %H:%M:%S GMT-03:00 %Y")
    return [token, expires_ISOND]

def request_basins(token):
    endpoint  = "/EstacoesTelemetricas/HidroBacia/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items = request_hidro_ws(endpoint, headers, {}).get("items", {})
        basins = []
        for item in items:
            basin = (
                item.get("Data_Ultima_Alteracao"),
                item.get("codigobacia"),
                item.get("Nome_Bacia")
            )
            basins.append(basin)
        return basins
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_sub_basins(token):
    endpoint  = "/EstacoesTelemetricas/HidroSubBacia/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items  = request_hidro_ws(endpoint, headers, {}).get("items", {})
        sub_basins = []
        for item in items:
            basin = (
                item.get("Data_Ultima_Alteracao"),
                item.get("codigosubbacia"),
                item.get("Bacia_Codigo"),
                item.get("Sub_Bacia_Nome").replace("'", "''")
            )
            sub_basins.append(basin)
        return sub_basins
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_entity(token):
    endpoint = "/EstacoesTelemetricas/HidroEntidade/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items  = request_hidro_ws(endpoint, headers, {}).get("items", {})
        entities = []
        for item in items:
            item = (
                item.get("Data_Ultima_Alteracao"),
                item.get("codigoentidade"),
                item.get("Entidade_Nome"),
                item.get("Entidade_Sigla")
            )
            entities.append(item)
        return entities
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_township(token):
    endpoint = "/EstacoesTelemetricas/HidroMunicipio/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items  = request_hidro_ws(endpoint, headers, {}).get("items", {})
        towns = []
        for item in items:
            item = (
                item.get("Data_Ultima_Alteracao"),
                item.get("Estado_Codigo"),
                item.get("Municipio_Codigo_IBGE"),
                item.get("Municipio_Nome").replace("'", "''"),
                item.get("codigomunicipio")
            )
            towns.append(item)
        return towns
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_rivers(token):
    endpoint = "/EstacoesTelemetricas/HidroRio/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items  = request_hidro_ws(endpoint, headers, {}).get("items", {})
        rivers = []
        for item in items:
            item = (
                item.get("Data_Ultima_Alteracao"),
                item.get("codigorio"),
                item.get("Bacia_Codigo"),
                item.get("Sub_Bacia_Codigo"),
                item.get("Nome_Rio").replace("'", "''"),
                item.get("Rio_Jurisdicao")
            )
            rivers.append(item)
        return rivers
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_states(token):
    endpoint = "/EstacoesTelemetricas/HidroUF/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    try:
        items  = request_hidro_ws(endpoint, headers, {}).get("items", {})
        states = []
        for item in items:
            item = (
                item.get("Data_Ultima_Alteracao"),
                item.get("codigouf"),
                item.get("Estado_Codigo_IBGE"),
                item.get("Estado_Sigla"),
                item.get("Estado_Nome").replace("'", "''")
            )
            states.append(item)
        return states
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_stations(token, UF):
    endpoint  = "/EstacoesTelemetricas/HidroInventarioEstacoes/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    params    = {"Unidade Federativa": f"{UF}"}
    try:
        file_path = f"./json/stations/Estacao_{UF}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                items = json.load(f)
        else:
            items = request_hidro_ws(endpoint, headers).get("items", {})
            with open(file_path, 'w') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        return [tuple(item.values()) for item in items]
    except Exception as e:
            print(f"Error (exception): {e}")
            return []

def request_rain_data(token, station_code, date_start, date_end):
    endpoint = "/EstacoesTelemetricas/HidroSerieChuva/v1"
    headers = {
        "accept":        "*/*",
        "Authorization": f"Bearer {token}"
    }
    [ymd_start, _] = date_start.split()
    [ymd_end, _] = date_end.split()
    params    = {
        "Código da Estação": station_code,
        "Tipo Filtro Data": "DATA_LEITURA", # "DATA_ULTIMA_ATUALIZACAO"
        "Data Inicial (yyyy-MM-dd)": f"{ymd_start}",
        "Data Final (yyyy-MM-dd)": f"{ymd_end}"
    }
    try:
        items = request_hidro_ws(endpoint, headers, params).get("items", {})
        return (True, [tuple(item.values()) for item in items])
    except Exception as e:
            print(f"Error (exception): {e}")
            return (False, [])
