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

import pytest
from unittest.mock import patch

from hidrodb.database import *
from hidrodb.database import _setup_db

DATABASE_PARAMS = [
    ("hidro.db",  'hidrodb.database.hidro.HIDRO_PATH',  DatabaseType.HIDRO),
    ("client.db", 'hidrodb.database.client.CLIENT_PATH', DatabaseType.CLIENT),
]

@pytest.fixture(params=DATABASE_PARAMS)
def db_connection(tmp_path, request):
    """Create a temporary database connection for testing."""

    filename, _, db_type = request.param
    db_path = str(tmp_path / filename)
    connection = DatabaseConnection(db_path, db_type)
    yield connection
    connection.close()

def test_init_db(tmp_path):
    """TODO."""

    import hidrodb.database.hidro as hidro
    import hidrodb.database.client as client
    assert hidro.HIDRO_DB is None
    assert client.CLIENT_DB is None
    hidro_path  = str(tmp_path / "hidro.db")
    client_path = str(tmp_path / "client.db")
    init_db(hidro_path, client_path)
    assert hidro.HIDRO_DB is not None
    assert client.CLIENT_DB is not None


def test_get_session_returns_session(db_connection):
    """Test that get_session returns a valid session."""

    session = db_connection.get_session()
    assert session is not None
    session.close()
