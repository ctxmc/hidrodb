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

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker, Session

from enum import StrEnum

class DatabaseType(StrEnum):
    """
    Enum to name databases
    """

    HIDRO  = "Hidro"
    CLIENT = "Client"

class DatabaseConnection:
    """ Class to hold database engine."""

    def __init__(self, dbq: str, db_type: DatabaseType):
        self.engine  = create_engine(f"sqlite:///{dbq}", echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.type    = db_type

    def get_session(self) -> Session:
        return self.Session()
    def close(self):
        self.engine.dispose()


def _setup_db(db_path, db_type) -> None:
    """ Setup an DatabaseConnection, if there is no tables, creates then"""

    db = DatabaseConnection(db_path, db_type)
    match db.type:
        case DatabaseType.HIDRO:
            from hidrodb.models.hidro import HidroBase
            HidroBase.metadata.create_all(db.engine)
        case DatabaseType.CLIENT:
            from hidrodb.models.client import ClientBase
            ClientBase.metadata.create_all(db.engine)
    return db


def init_db(hidro_path, client_path) -> None:
    """ Init an DatabaseConnection"""

    hidro.HIDRO_DB   = _setup_db(hidro_path, DatabaseType.HIDRO)
    client.CLIENT_DB = _setup_db(client_path, DatabaseType.CLIENT)
