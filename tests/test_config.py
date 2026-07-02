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


def test_setup_logger_creates_custom_levels(caplog):
    import logging;

    VERBOSE = 5
    hidrodb.config.LOG_LEVEL = VERBOSE
    hidrodb.config.setup_logger()
    caplog.set_level(VERBOSE)

    logging.getLogger().trace("trace message")
    assert "trace message" in caplog.text
    assert "TRACE" in caplog.text

    logging.getLogger().verbose("verbose message")
    assert "verbose message" in caplog.text
    assert "VERBOSE" in caplog.text
