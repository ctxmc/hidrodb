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

import jaydebeapi
import jpype
import msaccessdb
import os
from enum import Enum, StrEnum, auto
import getpass
from datetime import datetime

jpype.startJVM()
jpype.addClassPath('./UCanAccess-5.0.1.bin/ucanaccess-5.0.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-lang3-3.8.1.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/commons-logging-1.2.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/hsqldb-2.5.0.jar')
jpype.addClassPath('./UCanAccess-5.0.1.bin/lib/jackcess-3.0.1.jar')

class DatabaseType(StrEnum):
    HIDRO  = "Hidro"
    CLIENT = "Client"
    JOBS   = "Jobs"

class JobStatus(Enum):
    PENDING   = auto()
    FAILED    = auto()
    COMPLETED = auto()

class DatabaseConnection:
    def __init__(self, dbq: str, db_type: DatabaseType):
        self.connection = jaydebeapi.connect(
            'net.ucanaccess.jdbc.UcanaccessDriver',
            f'jdbc:ucanaccess://{dbq}',
            ['', '']
        )
        self.cursor = self.connection.cursor()
        self.type   = db_type

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

def init_db(db):
    meta   = db.connection.jconn.getMetaData()
    tables = meta.getTables(None, None, None, ["TABLE"])
    if not tables.next():
        print(f"No tables found for {db.type} Database. Initializing.")
        match db.type:
            case DatabaseType.HIDRO:
                execute_sql_file(db, "tables/hidro.sql")
                VERSION = '1.4.0.000'
                db.cursor.execute(f"INSERT INTO Versao (Versao) VALUES ('{VERSION}');")
                print(f"Initialized {db.type} Database Version {VERSION}.")
            case DatabaseType.CLIENT:
                execute_sql_file(db, "tables/client.sql")
                user_id  = input("Enter API username: ")
                password = getpass.getpass("Enter API password: ")
                db.cursor.execute("""INSERT INTO Credentials (ID, Password)"""
                                   f"""VALUES ('{user_id}', '{password}');""")
                print(f"Initialized {db.type} Database.")
            case DatabaseType.JOBS:
                execute_sql_file(db, "tables/jobs.sql")
                print(f"Initialized {db.type} Database.")
    else:
        print(f"{db.type} Database is Initialized.")

def execute_sql_file(db, sql_file_path):
    if not os.path.isfile(sql_file_path):
        print(f"Error: {sql_file_path} does not exists")
        return
    with open(sql_file_path, "r") as f:
        sql_script = f.read()
    statements = [s.strip() for s in sql_script.split(';') if s.strip()]
    for stmt in statements:
        db.connection.jconn.createStatement().execute(stmt)

def insert_basins(hidro, basins, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, code, name in basins:
        items.append((
            reg_id, 0, 0, 0, 0,
            code, name,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    Codigo, Nome, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_sub_basins(hidro, sub_basins, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, code, code_basin, name in sub_basins:
        items.append((
            reg_id, 0, 0, 0, 0,
            code_basin, code, name,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    BaciaCodigo, Codigo, Nome, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_entities(hidro, entities, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, code, name, acronym in entities:
        items.append((
            reg_id, 0, 0, 0, 0,
            code, name, acronym,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    Codigo, Nome, Sigla, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_towns(hidro, towns, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, state_code, IBGE_code, name, code in towns:
        items.append((
            reg_id, 0, 0, 0, 0,
            state_code, code, IBGE_code, name,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    EstadoCodigo, Codigo, CodigoIBGE, Nome, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_rivers(hidro, rivers, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, code, basin_code, sub_basin_code, name, jurisdiction in rivers:
        items.append((
            reg_id, 0, 0, 0, 0,
            basin_code, sub_basin_code,
            code, name, jurisdiction,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    BaciaCodigo, SubBaciaCodigo, Codigo, Nome, Jurisdicao, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_states(hidro, states, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for date_last_update, code, IBGE_code, acronym, name in states:
        items.append((
            reg_id, 0, 0, 0, 0,
            code, IBGE_code, acronym, name,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols   = """RegistroID, Importado, Temporario, Removido, ImportadoRepetido,
    Codigo, CodigoIBGE, Sigla, Nome, DataIns, DataAlt"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_stations(hidro, stations, table):
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    items = []
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # TODO: Find a smart and cleaner way to this, e.g ORM
    for altitude, drainage, basin_name, code_aditional, code_operator_uf, date_climatology_end, date_climatology_start, date_desc_liquid_end, date_desc_liquid_start, date_scale_end, date_scale_start, date_piezo_end, date_piezo_start, date_pluvi_end, date_pluvi_start, date_water_quality_end, date_water_quality_start, date_rain_registry_end, date_rain_registry_start, date_level_registry_end, date_level_registry_start, date_sediment_end, date_sediment_start, date_tank_evaporation_end, date_tank_evaporation_start, date_telemetric_end, date_telemetric_start, date_last_update, station_name, latitude, longitude, town_code, town_name, operator_code, operator_acronym, operator_sub_uf, operator, responsible_code, responsible_acronym, responsible_uf, river_code, river_name, sub_basin_code, sub_basin_name, station_type, station_type_climatology, station_type_desc_liquid, station_type_scale, station_type_piezo, station_type_pluvi, station_type_water_quality, station_type_registry_rain, station_type_registry_level, station_type_sediment, station_type_tank_evaporation, station_type_telemetric, network_type_basic, network_type_captation, network_type_flow_rate_class, network_type_watercourse, network_type_energetic, network_type_strategic, network_type_navigation, network_type_water_quality, network_type_sendiments, uf_acronym, uf_name, code_basin, station_code in stations:        
        hidro.cursor.execute(f"SELECT Codigo FROM Estado WHERE Sigla = '{uf_acronym}'")
        match station_type:
            case "Fluviometrica":
                station_type = 1
            case "Pluviometrica":
                station_type = 2
        state_code = hidro.cursor.fetchone()[0]
        items.append((
            reg_id, 0, 0, 0, 0,
            code_basin, sub_basin_code, river_code, town_code, state_code,
            responsible_code, responsible_uf,
            operator_code, code_operator_uf, operator_sub_uf, station_type,
            station_code, station_name, code_aditional,
            latitude, longitude, altitude, drainage,
            station_type_scale, station_type_registry_level, station_type_desc_liquid,
            station_type_sediment, station_type_water_quality, station_type_pluvi,
            station_type_registry_rain, station_type_tank_evaporation, station_type_climatology,
            station_type_piezo, station_type_telemetric,
            date_scale_start, date_scale_end, date_level_registry_start, date_level_registry_end,
            date_desc_liquid_start, date_desc_liquid_end, date_sediment_start,date_sediment_end,
            date_water_quality_start, date_water_quality_end, date_pluvi_start, date_pluvi_end,
            date_rain_registry_start, date_rain_registry_end,
            date_tank_evaporation_start, date_tank_evaporation_end,
            date_climatology_start, date_climatology_end,
            date_piezo_start, date_piezo_end,
            date_telemetric_start, date_telemetric_end,
            network_type_basic, network_type_energetic, network_type_navigation,
            network_type_watercourse, network_type_strategic, network_type_captation,
            network_type_sendiments, network_type_water_quality,
            network_type_flow_rate_class, date_last_update, operator,
            date_insertion, date_last_update
        ))
        reg_id += 1
    cols = (
        "RegistroID,  Importado, Temporario, Removido, ImportadoRepetido,"
        "BaciaCodigo, SubBaciaCodigo, RioCodigo, MunicipioCodigo, EstadoCodigo,"
        "ResponsavelCodigo, ResponsavelUnidade,"                   # ResponsavelJurisdicao,
        "OperadoraCodigo, OperadoraUnidade, OperadoraSubUnidade, TipoEstacao,"
        "Codigo, Nome, CodigoAdicional,"
        "Latitude, Longitude, Altitude, AreaDrenagem,"
        "TipoEstacaoEscala, TipoEstacaoRegistradorNivel, TipoEstacaoDescLiquida,"
        "TipoEstacaoSedimentos, TipoEstacaoQualAgua, TipoEstacaoPluviometro,"
        "TipoEstacaoRegistradorChuva, TipoEstacaoTanqueEvapo, TipoEstacaoClimatologica,"
        "TipoEstacaoPiezometria, TipoEstacaoTelemetrica,"
        "PeriodoEscalaInicio, PeriodoEscalaFim, PeriodoRegistradorNivelInicio, PeriodoRegistradorNivelFim,"
        "PeriodoDescLiquidaInicio, PeriodoDescLiquidaFim, PeriodoSedimentosInicio, PeriodoSedimentosFim,"
        "PeriodoQualAguaInicio, PeriodoQualAguaFim, PeriodoPluviometroInicio, PeriodoPluviometroFim,"
        "PeriodoRegistradorChuvaInicio, PeriodoRegistradorChuvaFim,"
        "PeriodoTanqueEvapoInicio, PeriodoTanqueEvapoFim,"
        "PeriodoClimatologicaInicio, PeriodoClimatologicaFim,"
        "PeriodoPiezometriaInicio, PeriodoPiezometriaFim,"
        "PeriodoTelemetricaInicio, PeriodoTelemetricaFim,"
        "TipoRedeBasica, TipoRedeEnergetica, TipoRedeNavegacao,"
        "TipoRedeCursoDagua, TipoRedeEstrategica, TipoRedeCaptacao,"
        "TipoRedeSedimentos, TipoRedeQualAgua,"
        "TipoRedeClasseVazao, UltimaAtualizacao, Operando,"
        # "Descricao, Historico, NumImagens,"
        "DataIns, DataAlt" # RespAlt"
    )
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", items)

def insert_rain_data(rain_data):
    hidro = DatabaseConnection("hidro.mdb", DatabaseType.HIDRO)
    table = "Chuvas"
    hidro.cursor.execute(f"SELECT MAX([RegistroID]) + 1 FROM {table}")
    reg_id = hidro.cursor.fetchone()[0]
    reg_id = 1 if reg_id is None else int(reg_id)
    date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chuva_sequence = ", ".join(f"Chuva{i:02d}{suffix}" for i in range(1, 32) for suffix in ("", "Status"))
    rain_data = [(reg_id+i, 0, 0, 0, 0, *rain, date_insertion)
             for i, rain in enumerate(rain_data)]
    cols   = f"""RegistroID, Importado, Temporario, Removido, ImportadoRepetido, {chuva_sequence},
    Data, DataAlt, DiaMaxima, Maxima, MaximaStatus, NivelConsistencia, NumDiasDeChuva, NumDiasDeChuvaStatus,
    TipoMedicaoChuvas, Total, TotalAnual, TotalAnualstatus, TotalStatus, EstacaoCodigo, DataIns"""
    values = ','.join('?' for _ in cols.split(','))
    hidro.cursor.executemany(f"INSERT INTO {table} ({cols}) VALUES ({values})", rain_data)
    hidro.close()

def insert_jobs(jobs, table):
    db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    db.cursor.executemany(f"INSERT INTO {table} (StationID, FromDate, ToDate, Status) VALUES (?, ?, ?, ?)", jobs)
    db.close()

def update_jobs(table, status, job_id):
    db = DatabaseConnection("jobs.mdb", DatabaseType.JOBS)
    db.cursor.execute(
        f"UPDATE [{table}] SET [Status] = '{status}' "
        f"WHERE [ID] = '{job_id}'"
    )
    db.close()
