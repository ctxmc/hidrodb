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
        except Exception as e:
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

def insert_table(hidro, table, table_rows, table_values):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    rows   = f"RegistroID, Importado, Temporario, Removido, ImportadoRepetido, {table_rows}"
    values = f"{reg_id}, 0, 0, 0, 0, {table_values}"
    hidro.cursor.execute(f"INSERT INTO {table} ({rows}) VALUES ({values});")

def check_table(hidro, client, table):
    hidro.cursor.execute(f"SELECT COUNT(*) FROM {table}")
    if (not hidro.cursor.fetchone()[0]):
        print(f"{table} has no Entries, requesting data")
        if (check_token(client)):
            client.cursor.execute("SELECT Token FROM Token")
            token = client.cursor.fetchone()[0]
            headers = {
                "accept":        "*/*",
                "Authorization": f"Bearer {token}"
            }
            match table:
                case "Bacia":
                    endpoint  = "/EstacoesTelemetricas/HidroBacia/v1"
                case "Entidade":
                    endpoint = "/EstacoesTelemetricas/HidroEntidade/v1"
                case "Municipio":
                    endpoint = "/EstacoesTelemetricas/HidroMunicipio/v1"
                case _:
                    print(f"TODO {table}")
                    return
            items = request_hidro_ws(endpoint, headers).get("items", {})
            for item in items:
                last_date = item.get("Data_Ultima_Alteracao")
                last_date = "NULL" if last_date is None else f"'{last_date}'"
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                match table:
                    case "Bacia":
                        code   = item.get("codigobacia")
                        name   = item.get("Nome_Bacia")
                        rows   = 'Codigo, Nome, DataIns, DataAlt'
                        values = f"'{code}', '{name}', '{time}', {last_date}"
                    case "Entidade":
                        code   = item.get("codigoentidade")
                        name   = item.get("Entidade_Nome")
                        sigla  = item.get("Entidade_Sigla")
                        rows   = 'Codigo, Sigla, Nome, DataIns, DataAlt'
                        values = f"'{code}', '{sigla}', '{name}', '{time}', {last_date}"
                    case "Municipio":
                        code_state = item.get("Estado_Codigo")
                        code_IBGE  = item.get("Municipio_Codigo_IBGE")
                        code_IBGE  = "NULL" if code_IBGE is None else f"'{code_IBGE}'"
                        name       = item.get("Municipio_Nome").replace("'", "''")
                        code       = item.get("codigomunicipio")
                        rows   = 'EstadoCodigo, Codigo, CodigoIBGE, Nome, DataIns, DataAlt'
                        values = f"'{code_state}', {code_IBGE}, '{code}', '{name}', '{time}', {last_date}"
                    case _:
                        print(f"TODO {table}")
                        return
                insert_table(hidro, table, rows, values)
    else:
        print(f"{table} has Entries; TODO")
        
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

    check_table(hidro, client, "Bacia")
    check_table(hidro, client, "Entidade")
    check_table(hidro, client, "Municipio")

    client.close()
    hidro.close()

if __name__ == "__main__":
    main()
