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

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

ClientBase = declarative_base()

class Credentials(ClientBase):
    __tablename__ = 'Credentials'

    RegistroID = Column(Integer, primary_key=True, autoincrement=True)
    ID         = Column(String, nullable=False)
    Password   = Column(String, nullable=False)

class Token(ClientBase):
    __tablename__ = 'Token'

    RegistroID   = Column(Integer, primary_key=True, autoincrement=True)
    CredentialID = Column(Integer, ForeignKey('Credentials.ID'), nullable=False)
    Token        = Column(String)
    Expires      = Column(DateTime)

class HidroJob(ClientBase):
    __abstract__ = True

    ID         = Column(Integer, primary_key=True, autoincrement=True)
    HidroTable = Column(String, nullable=False)
    Status     = Column(SmallInteger, nullable=False)

    def __iter__(self):
        yield from {
            "ID":         self.ID,
            "HidroTable": self.HidroTable,
            "Status":     self.Status.value
        }.items()

class StationJobs(HidroJob):
    __tablename__ = 'StationJobs'

    UF         = Column(String, nullable=False)
    LastCheck  = Column(DateTime)

    def __iter__(self):
        yield from super().__iter__()
        yield from {
            "UF":        self.UF,
            "LastCheck": self.LastCheck
        }.items()

    def to_params(self):
        return {"Unidade Federativa": f"{self.UF}"}

class SeriesJobs(HidroJob):
    __tablename__ = 'SeriesJobs'

    StationID  = Column(BigInteger, nullable=False)
    FromDate   = Column(DateTime, nullable=False)
    ToDate     = Column(DateTime, nullable=False)

    def __iter__(self):
        yield from super().__iter__()
        yield from {
            "StationID": self.StationID,
            "FromDate":  self.FromDate,
            "ToDate":    self.ToDate
        }.items()

    def to_params(self):
        return {
            "Código da Estação":         self.StationID,
            "Tipo Filtro Data":          "DATA_LEITURA", # "DATA_ULTIMA_ATUALIZACAO"
            "Data Inicial (yyyy-MM-dd)": f"{self.FromDate.strftime('%Y-%m-%d')}",
            "Data Final (yyyy-MM-dd)":   f"{self.ToDate.strftime('%Y-%m-%d')}"
        }
