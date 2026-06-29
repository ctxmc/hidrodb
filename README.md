# HidroDB

An python application tool to request and sync data from ANA Hidro WebServices.

## Setup

- Requires [sqlite3](https://sqlite.org/index.html).
- Setup your python enviroment and install dependencies:
``` shell
    pip install .
```

## Usage

```
python hidrodb --help
usage: hidrodb [-h] [--hidro HIDRO] [--client CLIENT] [--max-workers MAX_WORKERS] [--batch-size BATCH_SIZE] [--log-level {TRACE,VERBOSE,DEBUG,INFO,WARNING,ERROR}]

options:
  -h, --help            show this help message and exit
  --hidro HIDRO         Path to Hidro Database file
  --client CLIENT       Path to Client Database file
  --max-workers MAX_WORKERS
  --batch-size BATCH_SIZE
                        Batch size threshold to write job data on Hidro Database
  --log-level {TRACE,VERBOSE,DEBUG,INFO,WARNING,ERROR}
                        Set logging level

```

## Documentation

- [WebServices](https://github.com/ctxmc/hidrodb/wiki/webservices)
- [Database](https://github.com/ctxmc/hidrodb/wiki/database)
- [Hidro Models](https://github.com/ctxmc/hidrodb/wiki/hidro-models)
- [Client Models](https://github.com/ctxmc/hidrodb/wiki/client-models)
- [Config](https://github.com/ctxmc/hidrodb/wiki/config)
- [Jobs](https://github.com/ctxmc/hidrodb/wiki/jobs)
