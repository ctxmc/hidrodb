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

"""
Provides general config to HidroDB application.
"""

import logging

LOG_LEVEL = None

def setup_arguments():
    import argparse;
    parser = argparse.ArgumentParser()

    hidro_help_message = "Path to Hidro Database file"
    parser.add_argument('--hidro',       type=str, default='db/hidro.db', help=hidro_help_message)

    client_help_message = "Path to Client Database file"
    parser.add_argument('--client',      type=str, default='db/client.db', help=client_help_message)

    max_workers_help_message = "Maximum number of worker threads"
    parser.add_argument('--max-workers', type=int, default=10)

    batch_size_help_message = "Batch size threshold to write job data on Hidro Database"
    parser.add_argument('--batch-size',  type=int, default=1000, help=batch_size_help_message)

    parser.add_argument('--log-level', default='INFO', choices=['TRACE', 'VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Set logging level')

    args = parser.parse_args()

    global LOG_LEVEL
    LOG_LEVEL = args.log_level
    import hidrodb.jobs as jobs
    jobs.MAX_WORKERS = args.max_workers
    jobs.BATCH_SIZE  = args.batch_size
    import hidrodb.database as db
    db.CLIENT_PATH = args.client
    db.HIDRO_PATH  = args.hidro

def setup_logger():
    """ Setup logger object accross application. """

    TRACE = 15
    setattr(logging.Logger, 'trace', _make_logger(TRACE))
    logging.addLevelName(TRACE, 'TRACE')
    VERBOSE = 5
    setattr(logging.Logger, 'verbose', _make_logger(VERBOSE))
    logging.addLevelName(VERBOSE, 'VERBOSE')
    logging.basicConfig(
        level=LOG_LEVEL,
        format='[%(levelname)s]: %(message)s'
    )


def _make_logger(level):
    """ Helper method to create TRACE and VERBOSE logger modes. """

    def logger(self, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)
    return logger


def setup_database():
    """ Setup Hidro and Client Database. """

    import hidrodb.database as db
    db.init_db(db.CLIENT_PATH, db.DatabaseType.CLIENT)
    db.init_db(db.HIDRO_PATH,  db.DatabaseType.HIDRO)
    if not db.check_credentials():
        user_id = input("Enter API username: ")
        import getpass;
        password = getpass.getpass("Enter API password: ")
        db.insert_credentials(user_id, password)
