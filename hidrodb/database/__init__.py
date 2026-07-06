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

import logging
logger = logging.getLogger(__name__)

from sqlalchemy     import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from enum import StrEnum

from hidrodb.models.hidro  import *
from hidrodb.models.client import ClientBase


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
    session = db.get_session()
    check_tables_sql = text("SELECT name FROM sqlite_master WHERE type='table'")
    result = session.execute(check_tables_sql)
    tables = result.fetchall()
    session.close()
    if not tables:
        logger.info(f"No tables found for {db.type} Database. Initializing.")
        match db.type:
            case DatabaseType.HIDRO:
                HidroBase.metadata.create_all(db.engine)
            case DatabaseType.CLIENT:
                ClientBase.metadata.create_all(db.engine)
    return db


def init_db() -> None:
    """ Init an DatabaseConnection"""

    hidro.hidro_db   = _setup_db(hidro.HIDRO_PATH, DatabaseType.HIDRO)
    client.client_db = _setup_db(client.CLIENT_PATH, DatabaseType.CLIENT)
