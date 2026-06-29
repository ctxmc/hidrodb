import pytest

import hidrodb.config

def test_setup_arguments_defaults():
    """Test default argument values"""

    from unittest.mock import patch

    with patch('sys.argv', ['script_name']):
        import hidrodb.jobs, hidrodb.database

        hidrodb.config.setup_arguments()
        assert hidrodb.config.LOG_LEVEL     == 'INFO'
        assert hidrodb.jobs.MAX_WORKERS     == 10
        assert hidrodb.jobs.BATCH_SIZE      == 1000
        assert hidrodb.database.CLIENT_PATH == 'db/client.db'
        assert hidrodb.database.HIDRO_PATH  == 'db/hidro.db'
