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

from config import *

def main() -> None:
    client = DatabaseConnection(client_path, DatabaseType.CLIENT)
    hidro  = DatabaseConnection(hidro_path, DatabaseType.HIDRO)

    init_db(client)
    init_db(hidro)

    client.close()
    hidro.close()

    for resource in HidroResource:
        check_resource(resource)
    for job in JobConfig:
        check_job(job)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', choices=['TRACE', 'VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--hidro',       type=str, default='db/hidro.db')
    parser.add_argument('--client',      type=str, default='db/client.db')
    parser.add_argument('--max-workers', type=int, default=100)
    parser.add_argument('--batch-size',  type=int, default=10000)
    args = parser.parse_args()

    import builtins;
    builtins.hidro_path  = args.hidro
    builtins.client_path = args.client
    builtins.MAX_WORKERS = args.max_workers
    builtins.BATCH_SIZE  = args.batch_size

    builtins.TRACE = 15
    logging.addLevelName(TRACE, "TRACE")
    setattr(
        logging.Logger, 'trace',
        lambda self, msg, *args, **kwargs:
        self._log(TRACE, msg, args, **kwargs) if self.isEnabledFor(TRACE) else None
    )

    builtins.VERBOSE = 5
    logging.addLevelName(VERBOSE, "VERBOSE")
    setattr(
        logging.Logger, 'verbose',
        lambda self, msg, *args, **kwargs:
        self._log(VERBOSE, msg, args, **kwargs) if self.isEnabledFor(VERBOSE) else None
    )

    logging.basicConfig(
        level=args.log_level,
        format='[%(levelname)s]: %(message)s'
    )

    from database          import *
    from jobs              import *

    main()
