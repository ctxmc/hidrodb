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
from hidrodb.database import *

@pytest.fixture
def hidro_db(tmp_path):
    """Create a temporary database connection for testing."""

    hidro_path       = tmp_path / "hidro.db"
    hidro_connection = DatabaseConnection(str(hidro_path), DatabaseType.HIDRO)
    yield hidro_connection
    hidro_connection.close()

@pytest.fixture
def client_db(tmp_path):
    """Create a temporary database connection for testing."""

    client_path       = tmp_path / "client.db"
    client_connection = DatabaseConnection(str(client_path), DatabaseType.CLIENT)
    yield client_connection
    client_connection.close()


def test_get_session_returns_session(hidro_db, client_db):
    """Test that get_session returns a valid session."""

    hidro_session = hidro_db.get_session()
    assert hidro_session is not None
    hidro_session.close()

    client_session = client_db.get_session()
    assert client_session is not None
    client_session.close()
