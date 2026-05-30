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

