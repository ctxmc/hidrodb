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

@pytest.mark.parametrize("filename, patch_module, db_type", DATABASE_PARAMS)
def test_setup_db_creates_tables_when_empty(tmp_path, filename, patch_module, db_type):
    """Test that init_db creates tables when database is empty."""

    db_path = str(tmp_path / filename)
    connection = DatabaseConnection(db_path, db_type)
    session = connection.get_session()
    check_tables_sql = text("SELECT name FROM sqlite_master WHERE type='table'")
    result = session.execute(check_tables_sql)
    tables = result.fetchall()
    assert len(tables) == 0
    session.close()
    connection.close()

    with patch(patch_module, db_path):
        new_connection = _setup_db(db_path, db_type)
        session = new_connection.get_session()
        result = session.execute(check_tables_sql)
        tables = result.fetchall()
        assert len(tables) > 0
        session.close()
        new_connection.close()


@pytest.fixture(params=DATABASE_PARAMS)
def db_connection(tmp_path, request):
    """Create a temporary database connection for testing."""

    filename, _, db_type = request.param
    db_path = tmp_path / filename
    connection = DatabaseConnection(str(db_path), db_type)
    yield connection
    connection.close()


def test_get_session_returns_session(db_connection):
    """Test that get_session returns a valid session."""

    session = db_connection.get_session()
    assert session is not None
    session.close()
