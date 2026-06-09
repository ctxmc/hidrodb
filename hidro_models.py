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

from typing import Dict
from datetime import datetime

class AccessEntrie():
    def __init__(self, reg_id: int, **kwargs):
        self.fields = {
            "RegistroID":        reg_id,
            "Importado":         0,
            "Temporario":        0,
            "Removido":          0,
            "ImportadoRepetido": 0,
            "DataIns":           datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.fields.update(kwargs)

    def keys(self) -> str:
        return ", ".join(self.fields.keys())

    def data(self) -> tuple:
        return tuple(self.fields.values())

    def values(self) -> str:
        return ','.join('?' for _ in self.keys().split(','))


class Basin:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":    json.get("Nome_Bacia"),
            "Codigo":  json.get("codigobacia"),
            "DataAlt": json.get("Data_Ultima_Alteracao")
        }


class SubBasin:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":        json.get("Sub_Bacia_Nome"),
            "Codigo":      json.get("codigosubbacia"),
            "DataAlt":     json.get("Data_Ultima_Alteracao"),
            "BaciaCodigo": json.get("Bacia_Codigo")
        }


class Entity:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":    json.get("Entidade_Nome"),
            "Sigla":   json.get("Entidade_Sigla"),
            "Codigo":  json.get("codigoentidade"),
            "DataAlt": json.get("Data_Ultima_Alteracao")
        }


class Township:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":         json.get("Municipio_Nome"),
            "Codigo":       json.get("codigomunicipio"),
            "DataAlt":      json.get("Data_Ultima_Alteracao"),
            "CodigoIBGE":   json.get("Municipio_Codigo_IBGE"),
            "EstadoCodigo": json.get("Estado_Codigo")
        }


class River:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":           json.get("Nome_Rio"),
            "Codigo":         json.get("codigorio"),
            "DataAlt":        json.get("Data_Ultima_Alteracao"),
            "Jurisdicao":     json.get("Rio_Jurisdicao"),
            "BaciaCodigo":    json.get("Bacia_Codigo"),
            "SubBaciaCodigo": json.get("Sub_Bacia_Codigo")
        }
