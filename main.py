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
import argparse
import requests
import json
from datetime import datetime

from database import *

def request_hidro_ws(endpoint, headers):
    url      = "https://www.ana.gov.br/hidrowebservice"
    response = requests.get(f"{url}{endpoint}", headers=headers)
    if response.ok:
        try:
            return response.json()
        except e:
            print(f"Error: {e}")
    else:
        try:
            print(f"Error: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Error: response {response}")

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
    data = request_hidro_ws(endpoint, headers)
    token           = data.get("items", {}).get("tokenautenticacao")
    expires_RFC2822 = data.get("items", {}).get("validade")
    expires_ISOND   = datetime.strptime(expires_RFC2822, "%a %b %d %H:%M:%S GMT-03:00 %Y")
    return [token, expires_ISOND]

def check_token(client):
    client.cursor.execute("SELECT COUNT(*) FROM Token")
    if (not client.cursor.fetchone()[0]):
        print("No Token present, requesting.")
        token, expires = request_token(client)
        client.cursor.execute("""INSERT INTO Token (Token, Expires)"""
                              f"""VALUES ('{token}', '{expires}');""")
        return True
    else:
        client.cursor.execute("SELECT Expires FROM Token")
        expires_ISOND = client.cursor.fetchone()[0]
        expires_datetime = datetime.strptime(expires_ISOND, "%Y-%m-%d %H:%M:%S")
        if datetime.now() < expires_datetime:
            return True
        else:
            print("Token expired, requesting new.")
            token, expires = request_token(client)
            client.cursor.execute("""UPDATE [Token] SET"""
                                  f"""[Token]   = '{token}',"""
                                  f"""[Expires] = '{expires}'"""
                                  f"""WHERE [Expires] = '{expires_ISOND}';""")
            print("Token updated.")
            return True

def check_bacia(hidro, client):
    hidro.cursor.execute("SELECT COUNT(*) FROM Bacia")
    if (not hidro.cursor.fetchone()[0]):
        print("Bacia has no Entries, requesting data")
        if (check_token(client)):
            client.cursor.execute("SELECT Token FROM Token")
            token = client.cursor.fetchone()[0]
            endpoint = "/EstacoesTelemetricas/HidroBacia/v1"
            headers = {
                "accept":        "*/*",
                "Authorization": f"Bearer {token}"
            }
            items = request_hidro_ws(endpoint, headers).get("items", {})
            for item in items:
                hidro.cursor.execute("SELECT MAX([RegistroID]) + 1 FROM Bacia")
                reg_id = hidro.cursor.fetchone()[0]
                reg_id = 1 if reg_id is None else int(reg_id)
                code = item.get("codigobacia")
                name = item.get("Nome_Bacia")
                last_date = item.get("Data_Ultima_Alteracao")
                last_date = "NULL" if last_date is None else f"'{last_date}'"
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows = 'RegistroID, Importado, Temporario, Removido, ImportadoRepetido, Codigo, Nome, DataIns, DataAlt'
                values = f"{reg_id}, 0, 0, 0, 0, '{code}', '{name}', '{time}', {last_date}"
                hidro.cursor.execute(f"INSERT INTO Bacia ({rows}) VALUES ({values});")
    else:
        print("Bacia has Entries; TODO")

def check_entidade(hidro, client):
    hidro.cursor.execute("SELECT COUNT(*) FROM Entidade")
    if (not hidro.cursor.fetchone()[0]):
        print("Entidade has no Entries, requesting data")
        if (check_token(client)):
            client.cursor.execute("SELECT Token FROM Token")
            token = client.cursor.fetchone()[0]
            endpoint = "/EstacoesTelemetricas/HidroEntidade/v1"
            headers = {
                "accept":        "*/*",
                "Authorization": f"Bearer {token}"
            }
            items = request_hidro_ws(endpoint, headers).get("items", {})
            with open('entidade.json', 'w') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            for item in items:
                hidro.cursor.execute("SELECT MAX([RegistroID]) + 1 FROM Entidade")
                reg_id = hidro.cursor.fetchone()[0]
                reg_id = 1 if reg_id is None else int(reg_id)
                code      = item.get("codigoentidade")
                name      = item.get("Entidade_Nome")
                sigla     = item.get("Entidade_Sigla")
                last_date = item.get("Data_Ultima_Alteracao")
                last_date = "NULL" if last_date is None else f"'{last_date}'"
                time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rows      = 'RegistroID, Importado, Temporario, Removido, ImportadoRepetido, Codigo, Sigla, Nome, DataIns, DataAlt'
                values = f"{reg_id}, 0, 0, 0, 0, '{code}', '{sigla}', '{name}', '{time}', {last_date}"
                hidro.cursor.execute(f"INSERT INTO Entidade ({rows}) VALUES ({values});")
    else:
        print("Entidade has Entries; TODO")
        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hidro',  type=str, default='hidro.mdb')
    parser.add_argument('--client', type=str, default='client.mdb')
    args = parser.parse_args()

    create_db(args.client)
    client = DatabaseConnection(args.client, DatabaseType.CLIENT)
    init_db(client)

    create_db(args.hidro)
    hidro = DatabaseConnection(args.hidro, DatabaseType.HIDRO)
    init_db(hidro)

    check_bacia(hidro, client)
    check_entidade(hidro, client)

    client.close()
    hidro.close()

if __name__ == "__main__":
    main()
