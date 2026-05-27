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

import argparse
import os
import jaydebeapi
import jpype
import msaccessdb

jpype.startJVM()
jpype.addClassPath('./UCanAccess-5.0.1.bin/ucanaccess-5.0.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-lang3-3.8.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-logging-1.2.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/hsqldb-2.5.0.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/jackcess-3.0.1.jar')

class DatabaseConnection:
    def __init__(self, dbq: str):
        self.conn = jaydebeapi.connect(
            'net.ucanaccess.jdbc.UcanaccessDriver',
            f'jdbc:ucanaccess://{dbq}',
            ['', '']
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

def check_hidro(cursor, connection):
    meta = connection.jconn.getMetaData()
    tables = meta.getTables(None, None, None, ["TABLE"])
    while tables.next():
        name = tables.getString("TABLE_NAME")
        cursor.execute(f"SELECT COUNT(*) FROM [{name}]")
        count = int(cursor.fetchone()[0])
        print(f"{name}: {count} entries")
        if count > 0:
            cursor.execute(f"SELECT * FROM [{name}]")
            for row in cursor.fetchall():
                print(row)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hidro',  type=str, default='hidro.mdb')
    args = parser.parse_args()
    if not os.path.isfile(args.hidro):
        print(f"Error: {args.hidro} does not exist")
        print(f"Creating {args.hidro}")
        msaccessdb.create(args.hidro)
        # TODO: CREATE TABLES

    hidro = DatabaseConnection(args.hidro)
    check_hidro(hidro.cursor, hidro.conn)

    hidro.close()

if __name__ == "__main__":
    main()
