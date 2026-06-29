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


def test_setup_arguments_custum():
    """Test default argument values"""

    from unittest.mock import patch

    test_arguments = ['script_name',
                      '--log-level',   'DEBUG',
                      '--max-workers', '5',
                      '--batch-size',  '500',
                      '--hidro',       'custom/hidro.db',
                      '--client',      'custom/client.db']

    with patch('sys.argv', test_arguments):
        import hidrodb.jobs, hidrodb.database

        hidrodb.config.setup_arguments()
        assert hidrodb.config.LOG_LEVEL     == 'DEBUG'
        assert hidrodb.jobs.MAX_WORKERS     == 5
        assert hidrodb.jobs.BATCH_SIZE      == 500
        assert hidrodb.database.CLIENT_PATH == 'custom/client.db'
        assert hidrodb.database.HIDRO_PATH  == 'custom/hidro.db'
