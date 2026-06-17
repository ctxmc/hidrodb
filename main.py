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
from enum import StrEnum

class HidroResource(StrEnum):
    BASIN             = "Bacia"
    SUB_BASIN         = "SubBacia"
    ENTITY            = "Entidade"
    TOWNSHIP          = "Municipio"
    RIVER             = "Rio"
    STATE             = "Estado"
    STATION           = "Estacao"

    def get_model(self):
        mapping = {
            HidroResource.BASIN:     Basin,
            HidroResource.SUB_BASIN: SubBasin,
            HidroResource.ENTITY:    Entity,
            HidroResource.TOWNSHIP:  Township,
            HidroResource.RIVER:     River,
            HidroResource.STATE:     State,
            HidroResource.STATION:   Station,
        }
        return mapping[self]

    def get_endpoint(self):
        mapping = {
            HidroResource.BASIN:     HidroEndpoint.BASIN,
            HidroResource.SUB_BASIN: HidroEndpoint.SUB_BASIN,
            HidroResource.ENTITY:    HidroEndpoint.ENTITY,
            HidroResource.TOWNSHIP:  HidroEndpoint.TOWNSHIP,
            HidroResource.RIVER:     HidroEndpoint.RIVER,
            HidroResource.STATE:     HidroEndpoint.STATE,
            HidroResource.STATION:   HidroEndpoint.STATION,
        }
        return mapping[self]

def check_resource(resource):
    hidro_db = DatabaseConnection(hidro_path, DatabaseType.HIDRO)
    session  = hidro_db.get_session()
    model    = resource.get_model()
    endpoint = resource.get_endpoint()
    if (not session.query(model).count()):
        logger.info(f"{resource} has no Entries, requesting data")
        token = get_token()
        if (token):
            match resource:
                case HidroResource.STATION:
                    entries = []
                    states_uf = session.query(State.Sigla).filter(State.CodigoIBGE.isnot(None)).all()
                    for (UF,) in states_uf:
                        token = get_token()
                        if (token):
                            params = {"Unidade Federativa": f"{UF}"}
                            items = request_data(token, endpoint, params)
                            entries.extend([model.from_json(item) for item in items])
                case _:
                    entries = [model.from_json(item) for item in request_data(token, endpoint)]
            insert_hidro(hidro_db, entries)
    else:
        logger.debug(f"{resource} has Entries; TODO")
    session.close()
    hidro_db.close()

def main():
    client = DatabaseConnection(client_path, DatabaseType.CLIENT)
    hidro  = DatabaseConnection(hidro_path, DatabaseType.HIDRO)

    init_db(client)
    init_db(hidro)

    client.close()
    hidro.close()

    for resource in HidroResource:
        check_resource(resource)
    for job in HidroJob:
        check_job(job)
    # check_telemeter()

    import signal;
    os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--hidro',  type=str, default='db/hidro.db')
    parser.add_argument('--client', type=str, default='db/client.db')
    parser.add_argument('--max-workers', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=10000)
    args = parser.parse_args()

    import builtins;
    builtins.hidro_path  = args.hidro
    builtins.client_path = args.client
    builtins.MAX_WORKERS = args.max_workers
    builtins.BATCH_SIZE  = args.batch_size

    logging.basicConfig(
        level=args.log_level,
        format='[%(levelname)s]: %(message)s'
    )

    from database          import *
    from hidro_webservices import *
    from jobs              import *
    from models            import *

    main()
