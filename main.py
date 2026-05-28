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
        self.connection = jaydebeapi.connect(
            'net.ucanaccess.jdbc.UcanaccessDriver',
            f'jdbc:ucanaccess://{dbq}',
            ['', '']
        )
        self.cursor = self.connection.cursor()
        self.name   = dbq

    def close(self):
        self.cursor.close()
        self.connection.close()

def create_db(db_path):
    if not os.path.isfile(db_path):
        print(f"Error: {db_path} does not exists")
        print(f"Creating {db_path}")
        msaccessdb.create(db_path)
    else:
        print(f"{db_path} exists.")

def check_db(db):
    meta   = db.connection.jconn.getMetaData()
    tables = meta.getTables(None, None, None, ["TABLE"])
    if not tables.next():
        print(f"No tables found for {db.name}. Initializing.")
        init_hidro(db)
def init_hidro(db):
    with open("hidro.sql", "r") as f:
        sql_script = f.read()
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
    for stmt in statements:
        db.connection.jconn.createStatement().execute(stmt)
    db.cursor.execute("INSERT INTO Versao (Versao) VALUES ('1.4.0.000');")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hidro',  type=str, default='hidro.mdb')
    args = parser.parse_args()

    create_db(args.hidro)
    hidro = DatabaseConnection(args.hidro)
    check_db(hidro)

    hidro.close()

if __name__ == "__main__":
    main()
