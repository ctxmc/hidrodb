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

from hidrodb.database        import *
from hidrodb.database        import _setup_db
from hidrodb.database.client import *

@pytest.fixture
def client_db(tmp_path):
    """Create a temporary CLIENT database for testing."""

    db_path = str(tmp_path / "client.db")
    db_type = DatabaseType.CLIENT
    connection = _setup_db(db_path, db_type)
    with patch('hidrodb.database.client.client_db', connection):
        yield connection
        ClientBase.metadata.drop_all(connection.engine)
        connection.close()


def test_insert_credentials_creates_entry(client_db):

    insert_credentials(user_id="test_user", password="test_pass")
    session = client_db.get_session()
    result = session.query(Credentials).filter_by(ID="test_user").first()
    assert result is not None
    assert result.ID == "test_user"
    assert result.Password == "test_pass"
    session.close()


@pytest.mark.parametrize("table_name, expected_result", [
    ("Bacia",     BaseJobs), ("SubBacia",  BaseJobs),
    ("Entidade",  BaseJobs), ("Municipio", BaseJobs),
    ("Rio",       BaseJobs), ("Estado",    BaseJobs)
])
def test_get_job_model(client_db, table_name, expected_result):
    model = get_job_model(table_name)
    assert model == expected_result
