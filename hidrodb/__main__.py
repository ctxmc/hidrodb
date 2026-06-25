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

from config import *

def main() -> None:
    client = DatabaseConnection(CLIENT_PATH, DatabaseType.CLIENT)
    hidro  = DatabaseConnection(HIDRO_PATH, DatabaseType.HIDRO)
    init_db(client)
    init_db(hidro)
    client.close()
    hidro.close()

    for resource in HidroResource:
        check_resource(resource)

    for job_config in JobConfig:
        match job_config:
            case JobConfig.STATION:
                check_stations_jobs()
            case _:
                check_series_job(job_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', default='INFO', choices=['TRACE', 'VERBOSE', 'DEBUG', 'INFO', 'WARNING', 'ERROR'])
    parser.add_argument('--hidro',       type=str, default='db/hidro.db')
    parser.add_argument('--client',      type=str, default='db/client.db')
    parser.add_argument('--max-workers', type=int, default=100)
    parser.add_argument('--batch-size',  type=int, default=10000)
    args = parser.parse_args()

    import config;
    config.HIDRO_PATH  = args.hidro
    config.CLIENT_PATH = args.client
    config.MAX_WORKERS = args.max_workers
    config.BATCH_SIZE  = args.batch_size
    config.DEBUG_MODE  = args.debug_mode

    config.setup_logger(args.log_level)
    from database import *
    from jobs     import *

    main()
