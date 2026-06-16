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

import os
import argparse
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import text

def check_table(hidro, table):
    session = hidro.get_session()
    result  = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
    if (not result.fetchone()[0]):
        logger.info(f"{table} has no Entries, requesting data")
        token = get_token()
        if (token):
            match table:
                case HidroTable.BASIN:
                    data = [Basin(item)    for item in request_data(token, HidroEndpoint.BASIN)]
                case HidroTable.SUB_BASIN:
                    data = [SubBasin(item) for item in request_data(token, HidroEndpoint.SUB_BASIN)]
                case HidroTable.ENTITY:
                    data = [Entity(item)   for item in request_data(token, HidroEndpoint.ENTITY)]
                case HidroTable.TOWNSHIP:
                    data = [Township(item) for item in request_data(token, HidroEndpoint.TOWNSHIP)]
                case HidroTable.RIVER:
                    data = [River(item)    for item in request_data(token, HidroEndpoint.RIVER)]
                case HidroTable.STATE:
                    data = [State(item)    for item in request_data(token, HidroEndpoint.STATE)]
                case HidroTable.STATION:
                    data = []
                    result = session.execute(text("SELECT Sigla FROM Estado WHERE CodigoIBGE IS NOT NULL"))
                    for (UF,) in result.fetchall():
                        token = get_token()
                        if (token):
                            params = {"Unidade Federativa": f"{UF}"}
                            data.extend([Station(item) for item in
                                         request_data(token, HidroEndpoint.STATION, params)])
                case _:
                    logger.debug(f"TODO: {table}")
                    return
            insert_hidro(hidro, table, data)
    else:
        logger.debug(f"{table} has Entries; TODO")

def main():
    client = DatabaseConnection(client_path, DatabaseType.CLIENT)
    hidro  = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    jobs   = DatabaseConnection(jobs_path, DatabaseType.JOBS)

    init_db(client)
    init_db(hidro)
    init_db(jobs)

    client.close()
    jobs.close()

    for table in HidroTable:
        check_table(hidro, table)
    for job in HidroJob:
        check_job(job)

    check_telemeter()

    hidro.close()

    import signal;
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--hidro',  type=str, default='db/hidro.db')
    parser.add_argument('--client', type=str, default='db/client.db')
    parser.add_argument('--jobs',   type=str, default='db/jobs.db')
    args = parser.parse_args()

    import builtins;
    builtins.hidro_path  = args.hidro
    builtins.client_path = args.client
    builtins.jobs_path   = args.jobs

    logging.basicConfig(
        level=args.log_level,
        format='[%(levelname)s]: %(message)s'
    )

    from database          import *
    from hidro_webservices import *
    from jobs              import *
    from hidro_models      import *

    main()
