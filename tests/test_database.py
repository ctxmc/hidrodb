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
