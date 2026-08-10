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
""" Provides ORM models for Hidro Database. """

from sqlalchemy import (
    Column, Float, SmallInteger,
    BigInteger, Integer, String,
    DateTime, UniqueConstraint,
    ForeignKey
)
from sqlalchemy.orm import declarative_base

from datetime import datetime

HidroBase = declarative_base()
class HidroBaseModel(HidroBase):
    """ Abstract model to hold commom attributes to Hidro Models. """

    __abstract__ = True

    RegistroID = Column(Integer, primary_key=True, autoincrement=True)
    """int: unique record identifier."""

    DataIns    = Column(DateTime, default=datetime.now)
    """datetime: date of insertion of the record."""

    DataAlt    = Column(DateTime)
    """datetime: date of last modification of the record."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Basin(HidroBaseModel):
    """ Database model for storing Basins data. """

    __tablename__ = 'Bacia'

    Nome    = Column(String)
    """string: name of the hydrographic basin."""

    Codigo  = Column(Integer, unique=True)
    """int: unique identifier of hydrographic basin."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome    = json_data.get("Nome_Bacia"),
            Codigo  = json_data.get("codigobacia"),
            DataAlt = json_data.get("Data_Ultima_Alteracao")
        )


class SubBasin(HidroBaseModel):
    """ Database model for storing Sub Basins data. """

    __tablename__ = 'SubBacia'

    Nome        = Column(String)
    """string: name of the hydrographic sub-basin."""

    Codigo      = Column(Integer, unique=True)
    """int: unique identifier of hydrographic sub-basin."""

    BaciaCodigo = Column(Integer)
    """int: identifier of which basin the given sub-basin belongs."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome        = json_data.get("Sub_Bacia_Nome"),
            Codigo      = json_data.get("codigosubbacia"),
            DataAlt     = json_data.get("Data_Ultima_Alteracao"),
            BaciaCodigo = json_data.get("Bacia_Codigo")
        )


class Entity(HidroBaseModel):
    """ Database model for storing Entity data. """

    __tablename__ = 'Entidade'

    Nome    = Column(String)
    """string: name of the entity."""

    Sigla   = Column(String)
    """string: acronym of the entity."""

    Codigo  = Column(Integer, unique=True)
    """int: unique identifier of the entity."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome    = json_data.get("Entidade_Nome"),
            Sigla   = json_data.get("Entidade_Sigla"),
            Codigo  = json_data.get("codigoentidade"),
            DataAlt = json_data.get("Data_Ultima_Alteracao"),
        )


class Township(HidroBaseModel):
    """ Database model for storing Township data. """

    __tablename__ = 'Municipio'

    Nome       = Column(String)
    """string: name of the town. """

    Codigo     = Column(Integer, unique=True)
    """int: unique identifier of the town on Hidro."""

    CodigoIBGE = Column(Integer)
    """int: identifier of the town based on IBGE."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome       = json_data.get("Municipio_Nome"),
            Codigo     = json_data.get("codigomunicipio"),
            CodigoIBGE = json_data.get("Municipio_Codigo_IBGE"),
            DataAlt    = json_data.get("Data_Ultima_Alteracao"),
        )


class River(HidroBaseModel):
    """ Database model for storing Rivers data. """

    __tablename__ = 'Rio'

    Nome              = Column(String)
    """string: the name of the river. """

    Codigo            = Column(Integer, unique=True)
    """int: unique identifier of the river. """

    Jurisdicao        = Column(SmallInteger)
    """
    int: river jurisdiction.
    1 - Federal
    2 - State
    3 - Undefined
    """

    BaciaCodigo       = Column(Integer)
    """int: identifier of which basin the given river belongs."""

    SubBaciaCodigo    = Column(Integer)
    """int: identifier of which sub-basin the given river belongs."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome           = json_data.get("Nome_Rio"),
            Codigo         = json_data.get("codigorio"),
            DataAlt        = json_data.get("Data_Ultima_Alteracao"),
            Jurisdicao     = json_data.get("Rio_Jurisdicao"),
            BaciaCodigo    = json_data.get("Bacia_Codigo"),
            SubBaciaCodigo = json_data.get("Sub_Bacia_Codigo"),
        )


class State(HidroBaseModel):
    """ Database model for storing States data. """

    __tablename__ = 'Estado'

    Nome       = Column(String)
    """string: name of the state."""

    Sigla      = Column(String)
    """int: acronym of the state."""

    Codigo     = Column(Integer, unique=True)
    """int: unique identifier of the state on Hidro."""

    CodigoIBGE = Column(Integer)
    """int: identifier of the state on IBGE."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome       = json_data.get("Estado_Nome"),
            Sigla      = json_data.get("Estado_Sigla"),
            Codigo     = json_data.get("codigouf"),
            CodigoIBGE = json_data.get("Estado_Codigo_IBGE"),
            DataAlt    = json_data.get("Data_Ultima_Alteracao"),
        )


class Station(HidroBaseModel):
    """ Database model for storing Stations data. """

    __tablename__ = 'Estacao'

    Altitude                      = Column(Float)
    """float: altitude of the station. """

    AreaDrenagem                  = Column(Float)
    """float: drainage area of the station in km2."""

    CodigoAdicional               = Column(String(15))
    """string: original or additional identifier of the station."""

    OperadoraUnidade              = Column(Integer)
    """int: code of the operator unity of the station."""

    PeriodoDescLiquidaFim         = Column(SmallInteger)
    """datetime: final date of observation of discharge flow on the station."""

    PeriodoDescLiquidaInicio      = Column(SmallInteger)
    """datetime: final date of observation of discharge flow on the station."""

    PeriodoClimatologicaFim       = Column(DateTime)
    """datetime: final date of observation of climatology on the station."""

    PeriodoClimatologicaInicio    = Column(DateTime)
    """datetime: start date of observation of climatology on the station."""

    PeriodoEscalaFim              = Column(DateTime)
    """datetime: final date of observation of scale on the station."""

    PeriodoEscalaInicio           = Column(DateTime)
    """datetime: start date of observation of scale the station."""

    PeriodoPiezometriaFim         = Column(DateTime)
    """datetime: final date of observation of piezometry on the station."""

    PeriodoPiezometriaInicio      = Column(DateTime)
    """datetime: start date of observation of piezometry on the station."""

    PeriodoPluviometroFim         = Column(DateTime)
    """datetime: final date of observation of pluviometry on the station."""

    PeriodoPluviometroInicio      = Column(DateTime)
    """datetime: start date of observation of pluviometry on the station."""

    PeriodoQualAguaFim            = Column(DateTime)
    """datetime: final date of observation of water quality on the station."""

    PeriodoQualAguaInicio         = Column(DateTime)
    """datetime: start date of observation of water quality on the station."""

    PeriodoRegistradorChuvaFim    = Column(DateTime)
    """datetime: final date of observation of rain on the station."""

    PeriodoRegistradorChuvaInicio = Column(DateTime)
    """datetime: start date of observation of rain on the station."""

    PeriodoRegistradorNivelFim    = Column(DateTime)
    """datetime: final date of observation of level registry on the station."""

    PeriodoRegistradorNivelInicio = Column(DateTime)
    """datetime: start date of observation of level registry on the station."""

    PeriodoSedimentosFim          = Column(DateTime)
    """datetime: final date of observation of sediments on the station."""

    PeriodoSedimentosInicio       = Column(DateTime)
    """datetime: start date of observation of sediments on the station."""

    PeriodoTanqueEvapoFim         = Column(DateTime)
    """datetime: final date of observation of tank evaporation on the station."""

    PeriodoTanqueEvapoInicio      = Column(DateTime)
    """datetime: start date of observation of tank evaporation on the station."""

    PeriodoTelemetricaFim         = Column(DateTime)
    """datetime: final date of observation of telemetry on the station."""

    PeriodoTelemetricaInicio      = Column(DateTime)
    """datetime: start date of observation of telemetry on the station."""

    UltimaAtualizacao             = Column(DateTime)
    """ datetime: date of last alteration of station data."""

    Nome                          = Column(String(50))
    """string: name of the station."""

    Latitude                      = Column(Float)
    """float: latitude of the station."""

    Longitude                     = Column(Float)
    """float: longitude of the station."""

    MunicipioCodigo               = Column(Integer)
    """int: identifier of the town which the station is located."""

    EstadoCodigo                  = Column(Integer)
    """int: identifier of the state which the station is located."""

    OperadoraCodigo               = Column(BigInteger)
    """int: identifier of the operator of the station."""

    OperadoraSubUnidade           = Column(Integer)
    """int: identifier of the operator sub-unity of the station."""

    Operando                      = Column(SmallInteger)
    """int: identifies if the station still operating. 0 - No. 1 - Yes. """

    ResponsavelCodigo             = Column(BigInteger)
    """int: identifier of who owns jurisdiction over the station. """

    ResponsavelUnidade            = Column(Integer)
    """int: identifier of the unity which belongs the station. """

    RioCodigo                     = Column(BigInteger)
    """int: identifier of the river where is the station."""

    SubBaciaCodigo                = Column(BigInteger)
    """int: identifier of the sub-basin where is the station."""

    TipoEstacaoClimatologica      = Column(SmallInteger)
    """int: identifies if the station makes climatological measurements. 0 - No. 1 - Yes. """

    TipoEstacaoDescLiquida        = Column(SmallInteger)
    """int: identifies if the station makes discharge flow measurements. 0 - No. 1 - Yes. """

    TipoEstacao                   = Column(SmallInteger)
    """int: type of the station. 1 - Pluviometry. 2 - Fluviometry. """

    TipoEstacaoEscala             = Column(SmallInteger)
    """int: identifies if the station measures stage with scale. 0 - No. 1 - Yes. """

    TipoEstacaoPiezometria        = Column(SmallInteger)
    """int: identifies if the station makes piezometric measurements. 0 - No. 1 - Yes. """

    TipoEstacaoPluviometro        = Column(SmallInteger)
    """int: identifies if the station makes pluviometric measurements. 0 - No. 1 - Yes. """

    TipoEstacaoQualAgua           = Column(SmallInteger)
    """int: identifies if the station makes water quality measurements. 0 - No. 1 - Yes. """

    TipoEstacaoRegistradorChuva   = Column(SmallInteger)
    """int: identifies if the station makes rain registries measurements. 0 - No. 1 - Yes. """

    TipoEstacaoRegistradorNivel   = Column(SmallInteger)
    """int: identifies if the station measures stage with level registries. 0 - No. 1 - Yes. """

    TipoEstacaoSedimentos         = Column(SmallInteger)
    """int: identifies if the station makes sediments measurements. 0 - No. 1 - Yes. """

    TipoEstacaoTanqueEvapo        = Column(SmallInteger)
    """int: identifies if the station makes tank evaporation measurements. 0 - No. 1 - Yes. """

    TipoEstacaoTelemetrica        = Column(SmallInteger)
    """int: identifies if the station makes telemetric measurements. 0 - No. 1 - Yes. """

    TipoRedeBasica                = Column(SmallInteger)
    """int: identifies if the station is basic type. 0 - No. 1 - Yes. """

    TipoRedeCaptacao              = Column(SmallInteger)
    """
    int: identifies if the station has captation.
    0 - No.
    1 - Domestic use.
    2 - Industrial use.
    3 - Irrigation use.
    4 - Recreational use.
    5 - Fish farming.
    6 - Generation.
    7 - General.
    """

    TipoRedeClasseVazao           = Column(SmallInteger)
    """int:
    0 - No.
    1 - Observated flow rate.
    2 - Natural flow rate.
    3 - Equivalent flow rate.
    4 - Turbinated flow rate.
    5 - Poured flow rate.
    6 - Afluent flow rate.
    7 - Bottom flow rate.
    """

    TipoRedeCursoDagua            = Column(SmallInteger)
    """int:
    0 - No.
    1 - Water source.
    2 - Main course.
    3 - Afluent.
    4 - Sub-afluent.
    5 - Other afluent.
    6 - Storm drain.
    7 - Domestic sewer.
    8 - Industrial sewer.
    9 - Other.
    """

    TipoRedeEnergetica            = Column(SmallInteger)
    """int: identifies if the station is energy-related type. 0 - No. 1 - Yes. """

    TipoRedeEstrategica           = Column(SmallInteger)
    """int: identifies if the station is strategical type. 0 - No. 1 - Yes. """

    TipoRedeNavegacao             = Column(SmallInteger)
    """int: identifies if the station is navigational type. 0 - No. 1 - Yes. """

    TipoRedeQualAgua              = Column(SmallInteger)
    """int:
    0 - No.
    1 - Special.
    2 - Freshwater class 1
    3 - Freshwater class 2
    4 - Freshwater class 3
    5 - Freshwater class 4
    6 - Salt water (1)
    7 - Salt water (2)
    8 - Brackish water (1)
    9 - Brackish water (2)
    10 - No classification.
    """

    TipoRedeSedimentos            = Column(SmallInteger)
    """int: identifies if the station is sediment type. 0 - No. 1 - Yes. """

    BaciaCodigo                   = Column(BigInteger)
    """int: identifier of the basin where is the station."""

    Codigo                        = Column(BigInteger, unique=True)
    """int: unique identifier of the station."""

    @classmethod
    def from_json(cls, json_data: dict):
        station_type_json = json_data.get("Tipo_Estacao")
        match station_type_json:
            case "Fluviometrica":
                station_type = 1
            case "Pluviometrica":
                station_type = 2
            case _:
                raise ValueError(f"Unknown station type: {station_type_json}")
        return cls(
            Altitude                      = json_data.get("Altitude"),
            AreaDrenagem                  = json_data.get("Area_Drenagem"),
            CodigoAdicional               = json_data.get("Codigo_Adicional"),
            OperadoraUnidade              = json_data.get("Codigo_Operadora_Unidade_UF"),
            PeriodoClimatologicaFim       = json_data.get("Data_Periodo_Climatologica_Fim"),
            PeriodoClimatologicaInicio    = json_data.get("Data_Periodo_Climatologica_Inicio"),
            PeriodoDescLiquidaFim         = json_data.get("Data_Periodo_Desc_Liquida_Fim"),
            PeriodoDescLiquidaInicio      = json_data.get("Data_Periodo_Desc_liquida_Inicio"),
            PeriodoEscalaFim              = json_data.get("Data_Periodo_Escala_Fim"),
            PeriodoEscalaInicio           = json_data.get("Data_Periodo_Escala_Inicio"),
            PeriodoPiezometriaFim         = json_data.get("Data_Periodo_Piezometria_Fim"),
            PeriodoPiezometriaInicio      = json_data.get("Data_Periodo_Piezometria_Inicio"),
            PeriodoPluviometroFim         = json_data.get("Data_Periodo_Pluviometro_Fim"),
            PeriodoPluviometroInicio      = json_data.get("Data_Periodo_Pluviometro_Inicio"),
            PeriodoQualAguaFim            = json_data.get("Data_Periodo_Qual_Agua_Fim"),
            PeriodoQualAguaInicio         = json_data.get("Data_Periodo_Qual_Agua_Inicio"),
            PeriodoRegistradorChuvaFim    = json_data.get("Data_Periodo_Registrador_Chuva_Fim"),
            PeriodoRegistradorChuvaInicio = json_data.get("Data_Periodo_Registrador_Chuva_Inicio"),
            PeriodoRegistradorNivelFim    = json_data.get("Data_Periodo_Registrador_Nivel_Fim"),
            PeriodoRegistradorNivelInicio = json_data.get("Data_Periodo_Registrador_Nivel_Inicio"),
            PeriodoSedimentosFim          = json_data.get("Data_Periodo_Sedimento_Fim"),
            PeriodoSedimentosInicio       = json_data.get("Data_Periodo_Sedimento_Inicio"),
            PeriodoTanqueEvapoFim         = json_data.get("Data_Periodo_Tanque_Evapo_Fim"),
            PeriodoTanqueEvapoInicio      = json_data.get("Data_Periodo_Tanque_Evapo_Inicio"),
            PeriodoTelemetricaFim         = json_data.get("Data_Periodo_Telemetrica_Fim"),
            PeriodoTelemetricaInicio      = json_data.get("Data_Periodo_Telemetrica_Inicio"),
            UltimaAtualizacao             = json_data.get("Data_Ultima_Atualizacao"),
            Nome                          = json_data.get("Estacao_Nome"),
            Latitude                      = json_data.get("Latitude"),
            Longitude                     = json_data.get("Longitude"),
            MunicipioCodigo               = json_data.get("Municipio_Codigo"),
            OperadoraCodigo               = json_data.get("Operadora_Codigo"),
            OperadoraSubUnidade           = json_data.get("Operadora_Sub_Unidade_UF"),
            Operando                      = json_data.get("Operando"),
            ResponsavelCodigo             = json_data.get("Responsavel_Codigo"),
            ResponsavelUnidade            = json_data.get("Responsavel_Unidade_UF"),
            RioCodigo                     = json_data.get("Rio_Codigo"),
            SubBaciaCodigo                = json_data.get("Sub_Bacia_Codigo"),
            TipoEstacao                   = station_type,
            TipoEstacaoClimatologica      = json_data.get("Tipo_Estacao_Climatologica"),
            TipoEstacaoDescLiquida        = json_data.get("Tipo_Estacao_Desc_Liquida"),
            TipoEstacaoEscala             = json_data.get("Tipo_Estacao_Escala"),
            TipoEstacaoPiezometria        = json_data.get("Tipo_Estacao_Piezometria"),
            TipoEstacaoPluviometro        = json_data.get("Tipo_Estacao_Pluviometro"),
            TipoEstacaoQualAgua           = json_data.get("Tipo_Estacao_Qual_Agua"),
            TipoEstacaoRegistradorChuva   = json_data.get("Tipo_Estacao_Registrador_Chuva"),
            TipoEstacaoRegistradorNivel   = json_data.get("Tipo_Estacao_Registrador_Nivel"),
            TipoEstacaoSedimentos         = json_data.get("Tipo_Estacao_Sedimentos"),
            TipoEstacaoTanqueEvapo        = json_data.get("Tipo_Estacao_Tanque_evapo"),
            TipoEstacaoTelemetrica        = json_data.get("Tipo_Estacao_Telemetrica"),
            TipoRedeBasica                = json_data.get("Tipo_Rede_Basica"),
            TipoRedeCaptacao              = json_data.get("Tipo_Rede_Captacao"),
            TipoRedeClasseVazao           = json_data.get("Tipo_Rede_Classe_Vazao"),
            TipoRedeCursoDagua            = json_data.get("Tipo_Rede_Curso_Dagua"),
            TipoRedeEnergetica            = json_data.get("Tipo_Rede_Energetica"),
            TipoRedeEstrategica           = json_data.get("Tipo_Rede_Estrategica"),
            TipoRedeNavegacao             = json_data.get("Tipo_Rede_Navegacao"),
            TipoRedeQualAgua              = json_data.get("Tipo_Rede_Qual_Agua"),
            TipoRedeSedimentos            = json_data.get("Tipo_Rede_Sedimentos"),
            BaciaCodigo                   = json_data.get("codigobacia"),
            Codigo                        = json_data.get("codigoestacao"),
            # ?                           = json_data.get("Bacia_Nome"),
            # ?                           = json.get("Municipio_Nome"),
            # ?                           = json.get("Operadora_Sigla"),
            # ?                           = json.get("Rio_Nome"),
            # ?                           = json.get("Sub_Bacia_Nome"),            
            # ?                           = json.get("UF_Estacao"),
            # ?                           = json.get("UF_Nome_Estacao"),
        )


class Rain(HidroBaseModel):
    """ Database model for storing Rain data. """

    __tablename__  = 'Chuvas'


    __table_args__ = (
        UniqueConstraint('EstacaoCodigo', 'Data', name='uq_rain'),
    )

    Data                 = Column(DateTime)
    """ datetime: date of measurements. """

    DiaMaxima            = Column(SmallInteger)
    """ int: day where rained most. """

    Maxima               = Column(Float)
    """ float: maximum value of rain in the month """

    MaximaStatus         = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of maximum value.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Accumulated value.
    """

    NivelConsistencia    = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    NumDiasDeChuva       = Column(SmallInteger)
    """ int: number of days that rained in the month. """

    NumDiasDeChuvaStatus = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of rain days.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Accumulated value.
    """

    TipoMedicaoChuvas    = Column(SmallInteger)
    """
    int: indicates the measurement procedure.
    1 - Pluviometry.
    2 - Pluviograph.
    3 - Data logger.
    """

    Total                = Column(Float)
    """ float: total value of rain in month. """

    TotalAnual           = Column(Float)
    """ float: total vazlue of rain in the year. """

    TotalAnualStatus     = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of total year value of rain.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Accumulated value.
    """

    TotalStatus          = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of month value of rain.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Accumulated value.
    """

    EstacaoCodigo        = Column(BigInteger)
    """int: station code indifier of the registrie."""

    for i in range(1, 32):
        locals()[f'Chuva{i:02d}'] = Column(f'Chuva{i:02d}', Float)
        locals()[f'Chuva{i:02d}Status'] = Column(f'Chuva{i:02d}Status', SmallInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {
            'Data':                 json_data.get("Data_Hora_Dado"),
            'DataAlt':              json_data.get("Data_Ultima_Alteracao"),
            'DiaMaxima':            json_data.get("Dia_Maxima"),
            'Maxima':               json_data.get("Maxima"),
            'MaximaStatus':         json_data.get("Maxima_Status"),
            'NivelConsistencia':    json_data.get("Nivel_Consistencia"),
            'NumDiasDeChuva':       json_data.get("Numero_Dias_de_Chuva"),
            'NumDiasDeChuvaStatus': json_data.get("Numero_Dias_de_Chuva_Status"),
            'TipoMedicaoChuvas':    json_data.get("Tipo_Medicao_Chuvas"),
            'Total':                json_data.get("Total"),
            'TotalAnual':           json_data.get("Total_Anual"),
            'TotalAnualStatus':     json_data.get("Total_Anual_Status"),
            'TotalStatus':          json_data.get("Total_Status"),
            'EstacaoCodigo':        json_data.get("codigoestacao"),
        }
        for i in range(1, 32):
            kwargs[f'Chuva{i:02d}'] = json_data.get(f"Chuva_{i:02d}")
            kwargs[f'Chuva{i:02d}Status'] = json_data.get(f"Chuva_{i:02d}_Status")

        return cls(**kwargs)


class DischargeSummary(HidroBaseModel):
    """ Database model for storing Discharge Summary  data. """

    __tablename__ = 'ResumoDescarga'
    __table_args__ = (
        UniqueConstraint(
            'EstacaoCodigo',
            'Data',
            name='uq_discharge_summary'
        ),
    )

    AreaMolhada       = Column(Float)
    """ float: wet area of measurement. """

    Cota              = Column(Float)
    """ float: associated stage value of the discharge flow measurement. """

    Data              = Column(DateTime)
    """ datetime: date of measurements. """

    Largura           = Column(Float)
    """ float: width of measurement. """

    NivelConsistencia = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    Profundidade      = Column(Float)
    """ float: depth of measurement. """

    Vazao             = Column(Float)
    """ float: measured flow rate. """

    VelMedia          = Column(Float)
    """ float: average speed of the measurement. """

    EstacaoCodigo     = Column(BigInteger)
    """int: station code indifier of the registrie."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            AreaMolhada       = json_data.get("Area_Molhada (m2)"),
            Cota              = json_data.get("Cota (cm)"),
            Data              = json_data.get("Data_Hora_Dado"),
            DataAlt           = json_data.get("Data_Ultima_Alteracao"),
            Largura           = json_data.get("Largura (m)"),
            NivelConsistencia = json_data.get("Nivel_Consistencia"),
            Profundidade      = json_data.get("Profundidade (m)"),
            Vazao             = json_data.get("Vazao (m3/s)"),
            VelMedia          = json_data.get("Vel_Media (m/s)"),
            EstacaoCodigo     = json_data.get("codigoestacao"),
        )


class Sediments(HidroBaseModel):
    """ Database model for storing Sediments data. """

    __tablename__ = 'Sedimentos'
    __table_args__ = (
        UniqueConstraint('EstacaoCodigo', 'Data', name='uq_sediments'),
    )

    AreaMolhada                = Column(Float)
    """ float: wet area of corresponding discharge flow measurement. """

    ConcentracaoMatSuspensao   = Column(Float)
    """ float: quantity of sediments by water volume (mg/1) measured in a determinated section of a river. """

    ConcentracaoDaAmostraExtra = Column(Float)
    """ float: quantity of sediments by water volume (mg/1) measured in a determinated section of a river. """

    CondutividadeEletrica      = Column(Float)
    """ float: uS/cm at 20 celsius. """

    Cota                       = Column(Float)
    """ float: associated stage of the corresponding discharge flow measurement. """

    CotaDeMedicao              = Column(Float)
    """ float: associated stage of the corresponding discharge flow measurement. """

    Data                       = Column(DateTime)
    """ datetime: date of measurements. """

    DataLiq                    = Column(DateTime)
    """ datetime: date of corresponding discharge flow measurement. """

    Largura                    = Column(Float)
    """ float: width of the measurement. """

    NivelConsistencia          = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    NumMedicao                 = Column(BigInteger)
    """ int: number of measurement of sediments. """

    NumMedicaoLiq              = Column(BigInteger)
    """ int: number of corresponding discharge flow measurement. """

    Observacoes                = Column(String)
    """ string: observations of the measurement. """

    TemperaturaDaAgua          = Column(Float)
    """
    float: temperature of the water in Celsius measured with manual thermometer
    in contact with water sample in situ.
    """

    Vazao                      = Column(Float)
    """ float: associated flow of the corresponding discharge flow measurement. """

    Velmedia                   = Column(Float)
    """ float: average speed of the corresponding discharge flow measurement. """

    EstacaoCodigo              = Column(BigInteger)
    """int: station code indifier of the registrie."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            AreaMolhada                = json_data.get("Area_Molhada"),
            ConcentracaoMatSuspensao   = json_data.get("Concentracao_PPM"),
            ConcentracaoDaAmostraExtra = json_data.get("Concentracao_da_Amostra_Extra"),
            CondutividadeEletrica      = json_data.get("Condutividade_Eletrica"),
            Cota                       = json_data.get("Cota_cm"),
            CotaDeMedicao              = json_data.get("Cota_de_Mediacao"),
            Data                       = json_data.get("Data_Hora_Dado"),
            DataLiq                    = json_data.get("Data_Hora_Medicao_Liquida"),
            DataAlt                    = json_data.get("Data_Ultima_Alteracao"),
            Largura                    = json_data.get("Largura"),
            NivelConsistencia          = json_data.get("Nivel_Consistencia"),
            NumMedicao                 = json_data.get("Numero_Medicao"),
            NumMedicaoLiq              = json_data.get("Numero_Medicao_Liquida"),
            Observacoes                = json_data.get("Observacoes"),
            TemperaturaDaAgua          = json_data.get("Temperatura_da_Agua"),
            Vazao                      = json_data.get("Vazao_m3_s"),
            Velmedia                   = json_data.get("Vel_Media"),
            EstacaoCodigo              = json_data.get("codigoestacao")
        )


class Stage(HidroBaseModel):
    """ Database model for storing Stage data. """

    __tablename__ = 'Cotas'
    __table_args__ = (
        UniqueConstraint('EstacaoCodigo', 'Data', name='uq_stage'),
    )

    Data              = Column(DateTime)
    """ datetime: date of measurements. """

    DiaMaxima         = Column(SmallInteger)
    """ int: day with maximum measured stage value. """

    DiaMinima         = Column(SmallInteger)
    """ int: day with minimum measured stage value. """

    Maxima            = Column(Float)
    """ float: maximum measured stage value in the month. """

    MaximaStatus      = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of maximum value.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Dry spell.
    """

    Media             = Column(Float)
    """ float: average measured stage value in the month. """

    MediaAnual        = Column(Float)
    """ float: average measured stage value in the year. """

    MediaAnualStatus  = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of year average value.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Dry spell.
    """

    MediaStatus       = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of average value.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Dry spell.
    """

    MediaDiaria       = Column(SmallInteger)
    """
    int: indicates if the measurement is a daily average or snapshot.
    1 - Snapshot.
    2 - Daily average.
    """

    Minima            = Column(Float)
    """ float: minimum measured stage value in the month. """

    MinimaStatus      = Column(SmallInteger)
    """
    int: indicate availability, precision and reliability of minimum value.
    0 - No value.
    1 - Real value.
    2 - Estimated value.
    3 - Doubtful value.
    4 - Dry spell.
    """

    TipoMedicaoCotas  = Column(SmallInteger)
    """
    int: indicates measurement procedure.
    1 - Scale.
    2 - Linigraph.
    3 - Data logger.
    """

    EstacaoCodigo     = Column(BigInteger)
    """int: station code indifier of the registrie."""

    NivelConsistencia = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    for i in range(1, 32):
        locals()[f'Cota{i:02d}'] = Column(f'Cota{i:02d}', Float)
        locals()[f'Cota{i:02d}Status'] = Column(f'Cota{i:02d}Status', SmallInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {
            "Data":              json_data.get("Data_Hora_Dado"),
            "DataAlt":           json_data.get("Data_Ultima_Alteracao"),
            "DiaMaxima":         json_data.get("Dia_Maxima"),
            "DiaMinima":         json_data.get("Dia_Minima"),
            "Maxima":            json_data.get("Maxima"),
            "MaximaStatus":      json_data.get("Maxima_Status"),
            "Media":             json_data.get("Media"),
            "MediaAnual":        json_data.get("Media_Anual"),
            "MediaAnualStatus":  json_data.get("Media_Anual_Status"),
            "MediaStatus":       json_data.get("Media_Status"),
            "MediaDiaria":       json_data.get("Mediadiaria"),
            "Minima":            json_data.get("Minima"),
            "MinimaStatus":      json_data.get("Minima_Status"),
            "TipoMedicaoCotas":  json_data.get("Tipo_Medicao_Cotas"),
            "EstacaoCodigo":     json_data.get("codigoestacao"),
            "NivelConsistencia": json_data.get("nivelconsistencia")
        }
        for i in range(1, 32):
            kwargs[f"Cota{i:02d}"]       = json_data.get(f"Cota_{i:02d}")
            kwargs[f"Cota{i:02d}Status"] = json_data.get(f"Cota_{i:02d}_Status")

        return cls(**kwargs)


class DischargeFlow(HidroBaseModel):
    """ Database model for storing Discharge Flow data. """

    __tablename__ = 'CurvaDescarga'
    __table_args__ = (
        UniqueConstraint(
            'EstacaoCodigo',
            'NumeroCurva',
            'PeriodoValidadeInicio',
            'PeriodoValidadeFim',
            name='uq_discharge_flow'
        ),
    )

    CoefA                 = Column(Float)
    """ float: coefficient of the exponential equation. """

    CoefH0                = Column(Float)
    """ float: coefficient of the exponential equation. """

    CoefN                 = Column(Float)
    """ float: coefficient of the exponential equation. """

    CoefA0                = Column(Float)
    """ float: coefficient of the polynomial equation (linear, parabolic or cubic). """

    CoefA1                = Column(Float)
    """ float: coefficient of the polynomial equation (linear, parabolic or cubic). """

    CoefA2                = Column(Float)
    """ float: coefficient of the polynomial equation (linear, parabolic or cubic). """

    CoefA3                = Column(Float)
    """ float: coefficient of the polynomial equation (linear, parabolic or cubic). """

    CotaMaxima            = Column(Float)
    """ float: maximum valid stage for the discharge. """

    CotaMinima            = Column(Float)
    """ float: minimun valid stage for the discharge. """

    NivelConsistencia     = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    NumeroCurva           = Column(String(5))
    """string: number that identifies the discharge, e.g: 1/2, 2/2, 3/4, etc."""

    PeriodoValidadeFim    = Column(DateTime)
    """ datetime: final date of vality of the discharge. """

    PeriodoValidadeInicio = Column(DateTime)
    """ datetime: Initial date of vality of the discharge. """

    TabelaPassoCota       = Column(Float)
    """
    float: amount to be added incrementally to the minimum quota to obtain
    the quotas from the discharge table.
    """

    TipoCurva             = Column(SmallInteger)
    """
    int: indicates whether the curve should be represented by an equation or
    by a discharge table.
    1 - Equation.
    2 - Table.
    """

    TipoEquacao           = Column(SmallInteger)
    """
    int: Indicates the type of equation that represents the curve (in the case that the
    curve is represented by an equation).
    1 - Power.
    2 - Linear.
    3 - Parabolic.
    4 - Cubic.
    """

    EstacaoCodigo         = Column(BigInteger)
    """int: station code indifier of the registrie."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            CoefA                 = json_data.get("Coef_a"),
            CoefH0                = json_data.get("Coef_h0"),
            CoefN                 = json_data.get("Coef_n"),
            CoefA0                = json_data.get("Coefa_0"),
            CoefA1                = json_data.get("Coefa_1"),
            CoefA2                = json_data.get("Coefa_2"),
            CoefA3                = json_data.get("Coefa_3"),
            CotaMaxima            = json_data.get("Cota_Maxima"),
            CotaMinima            = json_data.get("Cota_Minima"),
            DataAlt               = json_data.get("Data_Ultima_Alteracao"),
            NivelConsistencia     = json_data.get("Nivel_Consistencia"),
            NumeroCurva           = json_data.get("Numero_Curva"),
            PeriodoValidadeFim    = json_data.get("Periodo_Validade_Fim"),
            PeriodoValidadeInicio = json_data.get("Periodo_Validade_Inicio"),
            TabelaPassoCota       = json_data.get("Tabela_Passo_Cota"),
            TipoCurva             = json_data.get("Tipo_Curva"),
            TipoEquacao           = json_data.get("Tipo_Equacao"),
            EstacaoCodigo         = json_data.get("codigoestacao")
        )


class WaterQuality(HidroBaseModel):
    """ Database model for storing Water Quality data. """

    __tablename__ = 'QualAgua'
    __table_args__ = (
        UniqueConstraint(
            'EstacaoCodigo',
            'Data',
            name='uq_qual_agua'
        ),
    )

    n245T                       = Column(Float)
    """ float: measured levels of 2,4,5-T. """

    n245TP                      = Column(Float)
    """ float: measured levels of 2,4,5-TP. """

    n246Triclorofenol           = Column(Float)
    """ float: measured levels of 2,4,6-Trichlorophenol. """

    Acido24Diclorofenoxiacetico = Column(Float)
    """ float: measured levels of 2,4-Dichlorophenoxyacetic acid. """

    Aldrin                      = Column(Float)
    """ float: measured levels of Aldrin. """

    AzinfosEtil                 = Column(Float)
    """ float: measured levels of Azinphos-ethyl. """

    Benzeno                     = Column(Float)
    """ float: measured levels of Benzene. """

    BenzoAPireno                = Column(Float)
    """ float: measured levels of Bezon[a]pyrene. """

    BHC                         = Column(Float)
    """ float: measured levels of BHC. """

    BifenilasPolicloradas       = Column(Float)
    """ float: measured levels of BPC. """

    Escherichia                 = Column(Float)
    """ float: measured levels of Escherichia. """

    Carbaril                    = Column(Float)
    """ float: measured levels of Carbaryl. """

    Clordano                    = Column(Float)
    """ float: measured levels of Chlordane. """

    DDEPP                       = Column(Float)
    """ float: measured levels of ?. """

    DDT                         = Column(Float)
    """ float: measured levels of DDT. """

    Demeton                     = Column(Float)
    """ float: measured levels of Demeton. """

    Diazinon                    = Column(Float)
    """ float: measured levels of Diazinon. """

    Dieldrin                    = Column(Float)
    """ float: measured levels of Dieldrin. """

    DodecacloroNonacloro        = Column(Float)
    """ float: measured levels of ?. """

    DySystonDisulfton           = Column(Float)
    """ float: measured levels of Dy-Syston Dissulfoton. """

    Endossulfan                 = Column(Float)
    """ float: measured levels of Endosulfan. """

    FitoplanctonQuantitativo    = Column(Float)
    """ float: measured levels of Phytoplankton. """

    Endrin                      = Column(Float)
    """ float: measured levels of Endrin. """

    EpoxidoHeptacloro           = Column(Float)
    """ float: measured levels of Heptachlor Epoxide. """

    Ethion                      = Column(Float)
    """ float: measured levels of Ethion. """

    Gution                      = Column(Float)
    """ float: measured levels of Gution. """

    Heptacloro                  = Column(Float)
    """ float: measured levels of Heptachlor. """

    Lindano                     = Column(Float)
    """ float: measured levels of Lindane. """

    Malation                    = Column(Float)
    """ float: measured levels of Malathion. """

    MetilParation               = Column(Float)
    """ float: measured levels of Parathion methyl. """

    Metoxicloro                 = Column(Float)
    """ float: measured levels of Methoxychlor. """

    Paration                    = Column(Float)
    """ float: measured levels of Parathion. """

    FosforoTotal                = Column(Float)
    """ float: measured levels of Phosprorus. """

    Pentaclorofenol             = Column(Float)
    """ float: measured levels of PCP. """

    Phosdrin                    = Column(Float)
    """ float: measured levels of Fosdrin. """

    TetracloretoCarbono         = Column(Float)
    """ float: measured levels of Caborn Tetrachloride. """

    Tetracloroeteno             = Column(Float)
    """ float: measured levels of Tetrachloroethylene. """

    Toxafeno                    = Column(Float)
    """ float: measured levels of Toxaphene. """

    Tricloroeteno               = Column(Float)
    """ float: measured levels of 1,1,2-Trichloroethane. """

    Algas                       = Column(Float)
    """ float: measured levels of Algae. """

    Amoniaco                    = Column(Float)
    """ float: measured levels of Ammonia. """

    BacteriasHeterotroficas     = Column(Float)
    """ float: measured levels of Heterotroph. """

    CloroResidual               = Column(Float)
    """ float: measured levels of Chlorine. """

    Nitratos                    = Column(Float)
    """ float: measured levels of Nitrates. """

    Colifagos                   = Column(Float)
    """ float: measured levels of Coliphage. """

    ContagemBacteriasPlaca      = Column(Float)
    """ float: measured levels of ?. """

    EnteroBacteriasPatogenicas  = Column(Float)
    """ float: measured levels of Enterobacter. """

    Fungos                      = Column(Float)
    """ float: measured levels of Fungae. """

    NitrogenioAlbuminoide       = Column(Float)
    """ float: measured levels of Albuminoid nitrogen. """

    Protozoarios                = Column(Float)
    """ float: measured levels of protozoa. """

    Salmonelas                  = Column(Float)
    """ float: measured levels of Salmonella. """

    ZooplanctonTotal            = Column(Float)
    """ float: measured levels of Zooplankton. """

    NitrogenioAmoniacal         = Column(Float)
    """ float: measured levels of Ammoniacal Nitrogen. """

    NitrogenioTotal             = Column(Float)
    """ float: measured levels of Nitrogen. """

    OrtofosfatoTotal            = Column(Float)
    """ float: measured levels of Orthophosphate. """

    OD                          = Column(Float)
    """ float: measured levels of OD. """

    pH                          = Column(Float)
    """ float: measured levels of pH. """

    SolDissolvidosTotais        = Column(Float)
    """ float: measured levels of dissolved solids. """

    AlcalinidadeTotal           = Column(Float)
    """ float: measured levels of Alkalines. """

    SolSuspensaoTotais          = Column(Float)
    """ float: measured levels of suspended solids. """

    TempAmostra                 = Column(Float)
    """ float: measured levels of sample temperature. """

    TempAr                      = Column(Float)
    """ float: measured levels of air temperature. """

    Transparencia               = Column(Float)
    """ float: measured levels of water transparecy. """

    Turbidez                    = Column(Float)
    """ float: measured levels of water turbity. """

    Acidez                      = Column(Float)
    """ float: measured levels of water acidity. """

    AlcalinidadeCO3             = Column(Float)
    """ float: measured levels of cabornate ions. """

    AlcalinidadeHCO3            = Column(Float)
    """ float: measured levels of bicarbonates. """

    AlcalinidadeOH              = Column(Float)
    """ float: measured levels of TODO. """

    Aluminiodissolvido          = Column(Float)
    """ float: measured levels of TODO. """

    CarbonoOrganicoTotal        = Column(Float)
    """ float: measured levels of TODO. """

    Aluminio                    = Column(Float)
    """ float: measured levels of TODO. """

    AmoniaNaoIonizavel          = Column(Float)
    """ float: measured levels of TODO. """

    Arsenio                     = Column(Float)
    """ float: measured levels of TODO. """

    Bario                       = Column(Float)
    """ float: measured levels of TODO. """

    Berilio                     = Column(Float)
    """ float: measured levels of TODO. """

    BismutoTotal                = Column(Float)
    """ float: measured levels of TODO. """

    Borodissolvido              = Column(Float)
    """ float: measured levels of TODO. """

    Boro                        = Column(Float)
    """ float: measured levels of TODO. """

    Cadmio                      = Column(Float)
    """ float: measured levels of TODO. """

    CalcioTotal                 = Column(Float)
    """ float: measured levels of TODO. """

    Cloretos                    = Column(Float)
    """ float: measured levels of TODO. """

    Chumbo                      = Column(Float)
    """ float: measured levels of TODO. """

    Cianetolivre                = Column(Float)
    """ float: measured levels of TODO. """

    Cianetos                    = Column(Float)
    """ float: measured levels of TODO. """

    Cobalto                     = Column(Float)
    """ float: measured levels of TODO. """

    Cobredissolvido             = Column(Float)
    """ float: measured levels of TODO. """

    Cobre                       = Column(Float)
    """ float: measured levels of TODO. """

    ColiformesFecais            = Column(Float)
    """ float: measured levels of TODO. """

    ColiformesTotais            = Column(Float)
    """ float: measured levels of TODO. """

    CompostosOrganoclorados     = Column(Float)
    """ float: measured levels of TODO. """

    CompostosOrganofosforados   = Column(Float)
    """ float: measured levels of TODO. """

    CondutividadeEletrica       = Column(Float)
    """ float: measured levels of TODO. """

    Cor                         = Column(Float)
    """ float: measured levels of TODO. """

    CromoHexavalente            = Column(Float)
    """ float: measured levels of TODO. """

    CromoTotal                  = Column(Float)
    """ float: measured levels of TODO. """

    CromoTrivalente             = Column(Float)
    """ float: measured levels of TODO. """

    Densidadecianobacterias     = Column(Float)
    """ float: measured levels of TODO. """

    Detergentes                 = Column(Float)
    """ float: measured levels of TODO. """

    Dureza                      = Column(Float)
    """ float: measured levels of TODO. """

    Durezamagnesio              = Column(Float)
    """ float: measured levels of TODO. """

    DurezaTotal                 = Column(Float)
    """ float: measured levels of TODO. """

    ColiformesTermotolerantes   = Column(Float)
    """ float: measured levels of TODO. """

    EstreptococosFecais         = Column(Float)
    """ float: measured levels of TODO. """

    FerroDissolvido             = Column(Float)
    """ float: measured levels of TODO. """

    FerroTotal                  = Column(Float)
    """ float: measured levels of TODO. """

    Fluoretos                   = Column(Float)
    """ float: measured levels of TODO. """

    FosfatoTotal                = Column(Float)
    """ float: measured levels of TODO. """

    Hidrocarbonetos             = Column(Float)
    """ float: measured levels of TODO. """

    IndiceFenois                = Column(Float)
    """ float: measured levels of TODO. """

    IQA                         = Column(Float)
    """ float: measured levels of TODO. """

    Litio                       = Column(Float)
    """ float: measured levels of TODO. """

    CondutividadeEspecifica     = Column(Float)
    """ float: measured levels of TODO. """

    MagnesioTotal               = Column(Float)
    """ float: measured levels of TODO. """

    Manganes                    = Column(Float)
    """ float: measured levels of TODO. """

    Mercurio                    = Column(Float)
    """ float: measured levels of TODO. """

    Niquel                      = Column(Float)
    """ float: measured levels of TODO. """

    Nitritos                    = Column(Float)
    """ float: measured levels of TODO. """

    NitrogenioOrganico          = Column(Float)
    """ float: measured levels of TODO. """

    NitrogenioTotalKJELDAHL     = Column(Float)
    """ float: measured levels of TODO. """

    OleosGraxas                 = Column(Float)
    """ float: measured levels of TODO. """

    ODsaturacao                 = Column(Float)
    """ float: measured levels of TODO. """

    PotassioTotal               = Column(Float)
    """ float: measured levels of TODO. """

    DBO                         = Column(Float)
    """ float: measured levels of TODO. """

    Prata                       = Column(Float)
    """ float: measured levels of TODO. """

    ParametroProfundidade       = Column(Float)
    """ float: measured levels of TODO. """

    Selenio                     = Column(Float)
    """ float: measured levels of TODO. """

    SilicaDissolvida            = Column(Float)
    """ float: measured levels of TODO. """

    SodioTotal                  = Column(Float)
    """ float: measured levels of TODO. """

    SolDissolvidosFixos         = Column(Float)
    """ float: measured levels of TODO. """

    SolDissolvidosVolateis      = Column(Float)
    """ float: measured levels of TODO. """

    SolSuspensaoFixos           = Column(Float)
    """ float: measured levels of TODO. """

    SolSuspensaoVolateis        = Column(Float)
    """ float: measured levels of TODO. """

    SolFixos                    = Column(Float)
    """ float: measured levels of TODO. """

    DescargaLiquida             = Column(Float)
    """ float: measured levels of TODO. """

    SolSedimentaveis            = Column(Float)
    """ float: measured levels of TODO. """

    SolTotais                   = Column(Float)
    """ float: measured levels of TODO. """

    SolVolateis                 = Column(Float)
    """ float: measured levels of TODO. """

    Sulfatos                    = Column(Float)
    """ float: measured levels of TODO. """

    Sulfetos                    = Column(Float)
    """ float: measured levels of TODO. """

    UranioTotal                 = Column(Float)
    """ float: measured levels of TODO. """

    Vanadio                     = Column(Float)
    """ float: measured levels of TODO. """

    Zinco                       = Column(Float)
    """ float: measured levels of TODO. """

    n11Dicloroeteno             = Column(Float)
    """ float: measured levels of TODO. """

    n12Dicloroetano             = Column(Float)
    """ float: measured levels of TODO. """

    DQO                         = Column(Float)
    """ float: measured levels of TODO. """

    Choveu                      = Column(SmallInteger)
    """ float: measured levels of TODO. """

    Data                        = Column(DateTime)
    """ datetime: date of measurements. """

    NivelConsistencia           = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    NumMedicao                  = Column(BigInteger)

    PosHorizColeta              = Column(SmallInteger)

    PosVertColeta               = Column(SmallInteger)

    Profundidade                = Column(Float)

    EstacaoCodigo               = Column(BigInteger)
    """int: station code indifier of the registrie."""

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            n245T                       = json_data.get("100_2_4_5_t_mgl"),
            n245TP                      = json_data.get("101_2_4_5_tp_mgl"),
            n246Triclorofenol           = json_data.get("102_2_4_6_Triclorofenol_mgl"),
            Acido24Diclorofenoxiacetico = json_data.get("103_Acido_2_4_Diclorofenoxiacetico_mgl"),
            Aldrin                      = json_data.get("104_Aldrin_mgl"),
            AzinfosEtil                 = json_data.get("105_Azinfosetil_mgl"),
            Benzeno                     = json_data.get("106_Benzeno_mgl"),
            BenzoAPireno                = json_data.get("107_Benzoapireno_mgl"),
            BHC                         = json_data.get("108_BHC_mgl"),
            BifenilasPolicloradas       = json_data.get("109_Bifenilaspolicloradas_mgl"),
            Escherichia                 = json_data.get("10_Escherichiacoli_ufc_100ml"),
            Carbaril                    = json_data.get("110_Carbaril_mgl"),
            Clordano                    = json_data.get("111_Clordano_mgl"),
            DDEPP                       = json_data.get("112_DDEPP_mgl"),
            DDT                         = json_data.get("113_DDT_mgl"),
            Demeton                     = json_data.get("114_Demeton_mgl"),
            Diazinon                    = json_data.get("115_Diazinon_mgl"),
            Dieldrin                    = json_data.get("116_Dieldrin_mgl"),
            DodecacloroNonacloro        = json_data.get("117_Dodecaclorononacloro_mgl"),
            DySystonDisulfton           = json_data.get("118_Dysystondisulfton_mgl"),
            Endossulfan                 = json_data.get("119_Endossulfan_mgl"),
            FitoplanctonQuantitativo    = json_data.get("11_Fitoplancton_Quantitativo_celulas_100ml"),
            Endrin                      = json_data.get("120_Endrin_mgl"),
            EpoxidoHeptacloro           = json_data.get("121_Epoxidoheptacloro_mgl"),
            Ethion                      = json_data.get("122_Ethion_mgl"),
            Gution                      = json_data.get("123_Gution_mgl"),
            Heptacloro                  = json_data.get("124_Heptacloro_mgl"),
            Lindano                     = json_data.get("125_Lindano_mgl"),
            Malation                    = json_data.get("126_Malation_mgl"),
            MetilParation               = json_data.get("127_Metilparation_mgl"),
            Metoxicloro                 = json_data.get("128_Metoxicloro_mgl"),
            Paration                    = json_data.get("129_Paration_mgl"),
            FosforoTotal                = json_data.get("12_Fosforo_Total_mgl)"),
            Pentaclorofenol             = json_data.get("130_Pentaclorofenol_mgl"),
            Phosdrin                    = json_data.get("131_Phosdrin_mgl"),
            TetracloretoCarbono         = json_data.get("132_Tetra_Cloreto_Carbono_mgl"),
            Tetracloroeteno             = json_data.get("133_Tetra_Cloro_Eteno_mgl"),
            Toxafeno                    = json_data.get("134_Toxafeno_mgl"),
            Tricloroeteno               = json_data.get("135_Tricloro_Eteno_mgl"),
            Algas                       = json_data.get("136_Algas_n_upa_ml"),
            Amoniaco                    = json_data.get("137_Amoniaco_mgl"),
            BacteriasHeterotroficas     = json_data.get("138_Bacterias_Heterotroficas_ufc_ml"),
            CloroResidual               = json_data.get("139_Cloro_Residual_mgl"),
            Nitratos                    = json_data.get("13_Nitratos_mgl_n)"),
            Colifagos                   = json_data.get("140_Colifagos_nmp_100ml"),
            ContagemBacteriasPlaca      = json_data.get("141_Contagem_Bacterias_Placa_ufc_ml"),
            EnteroBacteriasPatogenicas  = json_data.get("142_Entero_Bacterias_Patogenicas_n_org_ml"),
            Fungos                      = json_data.get("143_Fungos_ufc_ml"),
            NitrogenioAlbuminoide       = json_data.get("144_Nitrogenio_Albuminoide_mgl"),
            Protozoarios                = json_data.get("145_Protozoarios_n_org_ml"),
            Salmonelas                  = json_data.get("146_Salmonelas_nmp_ml"),
            ZooplanctonTotal            = json_data.get("147_Zooplanctontotal_n_org_ml"),
            NitrogenioAmoniacal         = json_data.get("14_Nitrogenio_Amoniacal_mgl"),
            NitrogenioTotal             = json_data.get("15_Nitrogenio_Total_mgl_n"),
            OrtofosfatoTotal            = json_data.get("16_Ortofosfato_Total_mgl_po4"),
            OD                          = json_data.get("17_OD_mgl_02"),
            pH                          = json_data.get("18_PH"),
            SolDissolvidosTotais        = json_data.get("19_Soldissolvidos_Totais_mgl"),
            AlcalinidadeTotal           = json_data.get("1_Alcalinidade_Total_mgl_caco3"),
            SolSuspensaoTotais          = json_data.get("20_Solsuspensao_Totais_mgl"),
            TempAmostra                 = json_data.get("21_Temperatura_Amostra_c"),
            TempAr                      = json_data.get("22_Tempar_c"),
            Transparencia               = json_data.get("23_Transparencia_m"),
            Turbidez                    = json_data.get("24_Turbidez_ntu"),
            Acidez                      = json_data.get("25_Acidez_mgl_caco3"),
            AlcalinidadeCO3             = json_data.get("26_Alcalinidade_CO3_mgl"),
            AlcalinidadeHCO3            = json_data.get("27_Alcalinidade_HCO3_mgl"),
            AlcalinidadeOH              = json_data.get("28_Alcalinidade_OH_mgl"),
            Aluminiodissolvido          = json_data.get("29_Aluminio_Dissolvido_mgl"),
            CarbonoOrganicoTotal        = json_data.get("2_Carbono_Organico_Total_mgl"),
            Aluminio                    = json_data.get("30_Aluminio_mgl_al"),
            AmoniaNaoIonizavel          = json_data.get("31_Amonia_Nao_Ionizavel_mgl_nh3"),
            Arsenio                     = json_data.get("32_Arsenio_mgl"),
            Bario                       = json_data.get("33_Bario_mgl_ba"),
            Berilio                     = json_data.get("34_Berilio_mgl"),
            BismutoTotal                = json_data.get("35_Bismuto_Total_mgl"),
            Borodissolvido              = json_data.get("36_Borodissolvido_mgl"),
            Boro                        = json_data.get("37_Boro_mgl_b"),
            Cadmio                      = json_data.get("38_Cadmio_mgl_cd"),
            CalcioTotal                 = json_data.get("39_Calcio_Total_mgl"),
            Cloretos                    = json_data.get("3_Cloretos_mgl_cl"),
            Chumbo                      = json_data.get("40_Chumbo_mgl"),
            Cianetolivre                = json_data.get("41_Cianeto_Livre_mgl"),
            Cianetos                    = json_data.get("42_Cianetos_mgl_cn"),
            Cobalto                     = json_data.get("43_Cobalto_mgl_co"),
            Cobredissolvido             = json_data.get("44_Cobre_Dissolvido_mgl"),
            Cobre                       = json_data.get("45_Cobre_mgl_cu"),
            ColiformesFecais            = json_data.get("46_Coliformes_Fecais_nmp_100ml"),
            ColiformesTotais            = json_data.get("47_Coliformes_Totais_nmp_100ml"),
            CompostosOrganoclorados     = json_data.get("48_Compostos_Organo_Clorados_mgl"),
            CompostosOrganofosforados   = json_data.get("49_Compostos_Organo_Fosforados_mgl"),
            CondutividadeEletrica       = json_data.get("50_Condutivida_de_Eletrica_us_cm_a_20c"),
            Cor                         = json_data.get("51_COR_mg_pt_col"),
            CromoHexavalente            = json_data.get("52_Cromo_Hexavalente_mgl"),
            CromoTotal                  = json_data.get("53_Cromo_Total_mgl_cr"),
            CromoTrivalente             = json_data.get("54_Cromo_Trivalente_mgl"),
            Densidadecianobacterias     = json_data.get("55_Densidade_Ciano_Bacterias_cel_ml"),
            Detergentes                 = json_data.get("56_Detergentes_mgl_las"),
            Dureza                      = json_data.get("57_Dureza_mgl_caco3"),
            Durezamagnesio              = json_data.get("58_Dureza_Magnesio_mgl_mgco3"),
            DurezaTotal                 = json_data.get("59_Dureza_Total_mgl"),
            ColiformesTermotolerantes   = json_data.get("5_Coliformes_Termo_Tolerantes_ufc_100ml"),
            EstreptococosFecais         = json_data.get("61_Estreptococos_Fecais_nmp_100ml"),
            FerroDissolvido             = json_data.get("62_Ferro_Dissolvido_mgl"),
            FerroTotal                  = json_data.get("63_Ferro_Total_mgl"),
            Fluoretos                   = json_data.get("64_Fluoretos_mgl"),
            FosfatoTotal                = json_data.get("65_Fosfato_Total_mgl"),
            Hidrocarbonetos             = json_data.get("66_Hidrocarbonetos_mgl"),
            IndiceFenois                = json_data.get("67_Indicefenois_mgl_c6h5oh"),
            IQA                         = json_data.get("68_IQA"),
            Litio                       = json_data.get("69_Litio_mgl"),
            CondutividadeEspecifica     = json_data.get("6_Condutividade_Especifica_25oc_us_cm_a_25c"),
            MagnesioTotal               = json_data.get("70_Magnesio_Total_mgl"),
            Manganes                    = json_data.get("71_Manganes_mgl"),
            Mercurio                    = json_data.get("72_Mercurio_mgl"),
            Niquel                      = json_data.get("73_Niquel_mgl"),
            Nitritos                    = json_data.get("74_Nitritos_mgl"),
            NitrogenioOrganico          = json_data.get("75_Nitrogenio_Organico_mgl"),
            NitrogenioTotalKJELDAHL     = json_data.get("76_Nitrogenio_Total_kjeldahl_mgl"),
            OleosGraxas                 = json_data.get("77_Oleos_graxas_mgl"),
            ODsaturacao                 = json_data.get("78_OD_perc_saturacao"),
            PotassioTotal               = json_data.get("79_Potassio_Total_mgl"),
            DBO                         = json_data.get("7_DBO_mgl_02)"),
            Prata                       = json_data.get("80_Prata_mgl"),
            ParametroProfundidade       = json_data.get("81_Parametro_Profundidade_m"),
            Selenio                     = json_data.get("82_Selenio_mgl"),
            SilicaDissolvida            = json_data.get("83_Silicadissolvida_mgl"),
            SodioTotal                  = json_data.get("84_Sodiototal_mgl"),
            SolDissolvidosFixos         = json_data.get("85_Soldissolvidos_Fixos_mgl_a_180c)"),
            SolDissolvidosVolateis      = json_data.get("86_Soldissolvidos_Volateis_mgl"),
            SolSuspensaoFixos           = json_data.get("87_Sol_Suspensao_Fixos_mgl"),
            SolSuspensaoVolateis        = json_data.get("88_Sol_Suspensao_Volateis_mgl"),
            SolFixos                    = json_data.get("89_Solfixos_mgl"),
            DescargaLiquida             = json_data.get("8_Descarga_Liquida_m3s"),
            SolSedimentaveis            = json_data.get("90_Sol_sedimentaveis_mgl"),
            SolTotais                   = json_data.get("91_Sol_totais_mgl"),
            SolVolateis                 = json_data.get("92_Sol_Volateis_mgl"),
            Sulfatos                    = json_data.get("93_Sulfatos_mgl"),
            Sulfetos                    = json_data.get("94_Sulfetos_mgl"),
            UranioTotal                 = json_data.get("95_Uranio_Total_mgl"),
            Vanadio                     = json_data.get("96_Vanadio_mgl"),
            Zinco                       = json_data.get("97_Zinco_mgl"),
            n11Dicloroeteno             = json_data.get("98_1_1_Dicloroeteno_mgl"),
            n12Dicloroetano             = json_data.get("99_1_2_Dicloroetano_mgl"),
            DQO                         = json_data.get("9_DQO_mgl_02)"),
            Choveu                      = json_data.get("Choveu"),
            Data                        = json_data.get("Data_Hora_Dado"),
            DataAlt                     = json_data.get("Data_Ultima_Alteracao"),
            NivelConsistencia           = json_data.get("Nilvel_ConsistÃªncia"),
            NumMedicao                  = json_data.get("Num_Medicao"),
            PosHorizColeta              = json_data.get("Posicao_Horizontal_Coleta"),
            PosVertColeta               = json_data.get("Posicao_Vertical_Coleta"),
            Profundidade                = json_data.get("Profundidade_m"),
            EstacaoCodigo               = json_data.get("codigoestacao")
        )


class WaterQualityStatus(HidroBaseModel):
    """ Database model for storing Water Quality Status data. """

    __tablename__ = 'QualAguaStatus'

    QualAguaID = Column(Integer, ForeignKey("QualAgua.RegistroID"), nullable=False)
    """ int: foreign water quality ientifier.  """
    
    locals().update({
        f'QualAgua{i:03d}Status': Column(f'QualAgua{i:03d}Status', SmallInteger)
        for i in range(1, 148)
    })

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {}
        kwargs["QualAguaID"] = json_data.get("Registro_ID")
        for i in range(1, 148):
            kwargs[f"QualAgua{i:03d}Status"] = json_data.get(f"{i}_Status")

        return cls(**kwargs)


class Granulometry(HidroBaseModel):
    """ Database model for storing Granulometry data. """

    __tablename__ = 'Granulometria'
    __table_args__ = (
        UniqueConstraint(
            'EstacaoCodigo',
            'Data',
            'HoraInicial',
            'HoraFinal',
            name='uq_granulometry'
        ),
    )

    EstacaoCodigo             = Column(BigInteger)
    """int: station code indifier of the registrie."""

    NivelConsistencia         = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    Data                      = Column(DateTime)
    """ datetime: date of measurements. """

    HoraInicial               = Column(DateTime)

    HoraFinal                 = Column(DateTime)

    Cota                      = Column(Float)

    Largura                   = Column(Float)

    TipoAmostra               = Column(SmallInteger)

    TipoColeta                = Column(String(50))

    TipoEquip                 = Column(String(50))

    ProfTotal                 = Column(Float)

    OrdemColeta               = Column(BigInteger)

    DistPTOInicial            = Column(Float)

    ChuvaUlt48                = Column(SmallInteger)

    MatFundo15_9              = Column(Float)

    MatFundo8_0               = Column(Float)

    MatFundo4_0               = Column(Float)

    MatFundo2_0               = Column(Float)

    MatFundo1_0               = Column(Float)

    MatFundo0_5               = Column(Float)

    MatFundo0_25              = Column(Float)

    MatFundo0_125             = Column(Float)

    MatFundo0_0625            = Column(Float)

    MatFundoArgila            = Column(Float)

    MatFundoSilte             = Column(Float)

    MatFundoAreia             = Column(Float)

    MatFundoPedregulho        = Column(Float)

    MatFundo0_0_a_0_0156      = Column(Float)

    MatFundo0_0157_a_0_02     = Column(Float)

    MatFundo0_0201_a_0_0625   = Column(Float)

    MatFundo0_0626_a_0_1250   = Column(Float)

    MatFundo0_1251_a_0_25     = Column(Float)

    MatFundo0_2501_a_0_5      = Column(Float)

    MatFundo0_501_a_1_0       = Column(Float)

    MatFundo1_0001_a_2_0      = Column(Float)

    MatFundo2_0001_a_4_0      = Column(Float)

    MatFundo4_0001_a_8_0      = Column(Float)

    MatFundo8_0001_a_16_000   = Column(Float)

    MatFundoD10               = Column(Float)

    MatFundoD16               = Column(Float)

    MatFundoD35               = Column(Float)

    MatFundoD50               = Column(Float)

    MatFundoD65               = Column(Float)

    MatFundoD84               = Column(Float)

    MatFundoD90               = Column(Float)

    MatArrasteVazao           = Column(Float)

    MatArrasteLargRio         = Column(Float)

    MatArrasteLargEquip       = Column(Float)

    MatArrastePesoMat         = Column(Float)

    MatArrasteVelMedia        = Column(Float)

    MatArrasteTempAgua        = Column(Float)

    MatArrasteTempAr          = Column(Float)

    MatArrasteTempoColeta     = Column(Float)

    MatArrasteArraste         = Column(Float)

    MatArraste15_9            = Column(Float)

    MatArraste8_0             = Column(Float)

    MatArraste4_0             = Column(Float)

    MatArraste2_0             = Column(Float)

    MatArraste1_0             = Column(Float)

    MatArraste0_5             = Column(Float)

    MatArraste0_25            = Column(Float)

    MatArraste0_125           = Column(Float)

    MatArraste0_0625          = Column(Float)

    MatArrasteArgila          = Column(Float)

    MatArrasteSilte           = Column(Float)

    MatArrasteAreia           = Column(Float)

    MatArrastePedregulho      = Column(Float)

    MatArraste0_0_a_0_0156    = Column(Float)

    MatArraste0_0157_a_0_02   = Column(Float)

    MatArraste0_0201_a_0_0625 = Column(Float)

    MatArraste0_0626_a_0_1250 = Column(Float)

    MatArraste0_1251_a_0_25   = Column(Float)

    MatArraste0_2501_a_0_5    = Column(Float)

    MatArraste0_501_a_1_0     = Column(Float)

    MatArraste1_0001_a_2_0    = Column(Float)

    MatArraste2_0001_a_4_0    = Column(Float)

    MatArraste4_0001_a_8_0    = Column(Float)

    MatArraste8_0001_a_16_000 = Column(Float)

    MatArrasteD10             = Column(Float)

    MatArrasteD16             = Column(Float)

    MatArrasteD35             = Column(Float)

    MatArrasteD50             = Column(Float)

    MatArrasteD65             = Column(Float)

    MatArrasteD84             = Column(Float)

    MatArrasteD90             = Column(Float)

    MatSusp15_9               = Column(Float)

    MatSusp8_0                = Column(Float)

    MatSusp4_0                = Column(Float)

    MatSusp2_0                = Column(Float)

    MatSusp1_0                = Column(Float)

    MatSusp0_5                = Column(Float)

    MatSusp0_25               = Column(Float)

    MatSusp0_125              = Column(Float)

    MatSusp0_0625             = Column(Float)

    MatSuspArgila             = Column(Float)

    MatSuspSilte              = Column(Float)

    MatSuspAreia              = Column(Float)

    MatSuspPedregulho         = Column(Float)

    MatSusp0_0_a_0_0156       = Column(Float)

    MatSusp0_0157_a_0_02      = Column(Float)

    MatSusp0_0201_a_0_0625    = Column(Float)

    MatSusp0_0626_a_0_1250    = Column(Float)

    MatSusp0_1251_a_0_25      = Column(Float)

    MatSusp0_2501_a_0_5       = Column(Float)

    MatSusp0_501_a_1_0        = Column(Float)

    MatSusp1_0001_a_2_0       = Column(Float)

    MatSusp2_0001_a_4_0       = Column(Float)

    MatSusp4_0001_a_8_0       = Column(Float)

    MatSusp8_0001_a_16_000    = Column(Float)

    MatSuspD10                = Column(Float)

    MatSuspD16                = Column(Float)

    MatSuspD35                = Column(Float)

    MatSuspD50                = Column(Float)

    MatSuspD65                = Column(Float)

    MatSuspD84                = Column(Float)

    MatSuspD90                = Column(Float)


    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            EstacaoCodigo             = json_data.get("codigoestacao"),
            NivelConsistencia         = json_data.get("Nivel_Consistencia"),
            Data                      = json_data.get("Data_Dado"),
            HoraInicial               = json_data.get("Hora_Final"),
            HoraFinal                 = json_data.get("Hora_Inicial"),
            Cota                      = json_data.get("Cota_cm"),
            Largura                   = json_data.get("Largura_m"),
            TipoAmostra               = json_data.get("Tipo_Amostra"),
            TipoColeta                = json_data.get("Tipo_Coleta"),
            TipoEquip                 = json_data.get("Tipo_Equip"),
            ProfTotal                 = json_data.get("Prof_Total_m"),
            OrdemColeta               = json_data.get("Ordem_Coleta"),
            DistPTOInicial            = json_data.get("Dist_Pto_Inicial_m"),
            ChuvaUlt48                = json_data.get("Chuva_Ult_48h"),
            MatFundo15_9              = json_data.get("MatFundo_15_9_mm"),
            MatFundo8_0               = json_data.get("MatFundo_8_0_mm"),
            MatFundo4_0               = json_data.get("MatFundo_4_0_mm"),
            MatFundo2_0               = json_data.get("MatFundo_2_0_mm"),
            MatFundo1_0               = json_data.get("MatFundo_1_0_mm"),
            MatFundo0_5               = json_data.get("MatFundo_0_5_mm"),
            MatFundo0_25              = json_data.get("MatFundo_0_25_mm"),
            MatFundo0_125             = json_data.get("MatFundo_0_125_mm"),
            MatFundo0_0625            = json_data.get("MatFundo_0_625_mm"),
            MatFundoArgila            = json_data.get("MatFundo_Argila_%"),
            MatFundoSilte             = json_data.get("MatFundo_Silte_%"),
            MatFundoAreia             = json_data.get("MatFundo_Areia_%"),
            MatFundoPedregulho        = json_data.get("MatFundo_Pedregulho_%"),
            MatFundo0_0_a_0_0156      = json_data.get("MatFundo_0_0_a_0_0156_mm"),
            MatFundo0_0157_a_0_02     = json_data.get("MatFundo_0_0157_a_0_02_mm"),
            MatFundo0_0201_a_0_0625   = json_data.get("MatFundo_0_0201_a_0_0625_mm"),
            MatFundo0_0626_a_0_1250   = json_data.get("MatFundo_0_0626_a_0_1250_mm"),
            MatFundo0_1251_a_0_25     = json_data.get("MatFundo_0_1251_a_0_25_mm"),
            MatFundo0_2501_a_0_5      = json_data.get("MatFundo_0_2501_a_0_5_mm"),
            MatFundo0_501_a_1_0       = json_data.get("MatFundo_0_501_a_1_0_mm"),
            MatFundo1_0001_a_2_0      = json_data.get("MatFundo_1_0001_a_2_0_mm"),
            MatFundo2_0001_a_4_0      = json_data.get("MatFundo_2_0001_a_4_0_mm"),
            MatFundo4_0001_a_8_0      = json_data.get("MatFundo_4_0001_a_8_0_mm"),
            MatFundo8_0001_a_16_000   = json_data.get("MatFundo_8_0001_a_16_000_mm"),
            MatFundoD10               = json_data.get("MatFundo_D10_mm"),
            MatFundoD16               = json_data.get("MatFundo_D16_mm"),
            MatFundoD35               = json_data.get("MatFundo_D35_mm"),
            MatFundoD50               = json_data.get("MatFundo_D50_mm"),
            MatFundoD65               = json_data.get("MatFundo_D65_mm"),
            MatFundoD84               = json_data.get("MatFundo_D84_mm"),
            MatFundoD90               = json_data.get("MatFundo_D90_mm"),
            MatArrasteVazao           = json_data.get("MatArraste_Vazao_m3_s"),
            MatArrasteLargRio         = json_data.get("MatArraste_LargRio_m"),
            MatArrasteLargEquip       = json_data.get("MatArraste_LargEquip_m"),
            MatArrastePesoMat         = json_data.get("MatArraste_PesoMat_g"),
            MatArrasteVelMedia        = json_data.get("MatArraste_VelMedia_m_s"),
            MatArrasteTempAgua        = json_data.get("MatArraste_TempAgua_C"),
            MatArrasteTempAr          = json_data.get("MatArraste_TempAr_C"),
            MatArrasteTempoColeta     = json_data.get("MatArraste_TempoColeta_min"),
            MatArrasteArraste         = json_data.get("MatArraste_Arraste_t_dia"),
            MatArraste15_9            = json_data.get("MatArraste_15_9_mm"),
            MatArraste8_0             = json_data.get("MatArraste_8_0_mm"),
            MatArraste4_0             = json_data.get("MatArraste_4_0_mm"),
            MatArraste2_0             = json_data.get("MatArraste_2_0_mm"),
            MatArraste1_0             = json_data.get("MatArraste_1_0_mm"),
            MatArraste0_5             = json_data.get("MatArraste_0_5_mm"),
            MatArraste0_25            = json_data.get("MatArraste_0_25_mm"),
            MatArraste0_125           = json_data.get("MatArraste_0_125_mm"),
            MatArraste0_0625          = json_data.get("MatArraste_0_0625_mm"),
            MatArrasteArgila          = json_data.get("MatArraste_Argila_%"),
            MatArrasteSilte           = json_data.get("MatArraste_Silte_%"),
            MatArrasteAreia           = json_data.get("MatArraste_Areia_%"),
            MatArrastePedregulho      = json_data.get("MatArraste_Pedregulho_%"),
            MatArraste0_0_a_0_0156    = json_data.get("MatArraste_0_0_a_0_0156_mm"),
            MatArraste0_0157_a_0_02   = json_data.get("MatArraste_0_0157_a_0_02_mm"),
            MatArraste0_0201_a_0_0625 = json_data.get("MatArraste_0_0201_a_0_0625_mm"),
            MatArraste0_0626_a_0_1250 = json_data.get("MatArraste_0_0626_a_0_1250_mm"),
            MatArraste0_1251_a_0_25   = json_data.get("MatArraste_0_1251_a_0_25_mm"),
            MatArraste0_2501_a_0_5    = json_data.get("MatArraste_0_2501_a_0_5_mm"),
            MatArraste0_501_a_1_0     = json_data.get("MatArraste_0_501_a_1_0_mm"),
            MatArraste1_0001_a_2_0    = json_data.get("MatArraste_1_0001_a_2_0_mm"),
            MatArraste2_0001_a_4_0    = json_data.get("MatArraste_2_0001_a_4_0_mm"),
            MatArraste4_0001_a_8_0    = json_data.get("MatArraste_4_0001_a_8_0_mm"),
            MatArraste8_0001_a_16_000 = json_data.get("MatArraste_8_0001_a_16_000_mm"),
            MatArrasteD10             = json_data.get("MatArraste_D10_mm"),
            MatArrasteD16             = json_data.get("MatArraste_D16_mm"),
            MatArrasteD35             = json_data.get("MatArraste_D35_mm"),
            MatArrasteD50             = json_data.get("MatArraste_D50_mm"),
            MatArrasteD65             = json_data.get("MatArraste_D65_mm"),
            MatArrasteD84             = json_data.get("MatArraste_D84_mm"),
            MatArrasteD90             = json_data.get("MatArraste_D90_mm"),
            MatSusp15_9               = json_data.get("MatSusp_15_9_mm"),
            MatSusp8_0                = json_data.get("MatSusp_8_0_mm"),
            MatSusp4_0                = json_data.get("MatSusp_4_0_mm"),
            MatSusp2_0                = json_data.get("MatSusp_2_0_mm"),
            MatSusp1_0                = json_data.get("MatSusp_1_0_mm"),
            MatSusp0_5                = json_data.get("MatSusp_0_5_mm"),
            MatSusp0_25               = json_data.get("MatSusp_0_25_mm"),
            MatSusp0_125              = json_data.get("MatSusp_0_125_mm"),
            MatSusp0_0625             = json_data.get("MatSusp_0_0625_mm"),
            MatSuspArgila             = json_data.get("MatSusp_Argila_%"),
            MatSuspSilte              = json_data.get("MatSusp_Silte_%"),
            MatSuspAreia              = json_data.get("MatSusp_Areia_%"),
            MatSuspPedregulho         = json_data.get("MatSusp_Pedregulho_%"),
            MatSusp0_0_a_0_0156       = json_data.get("MatSusp_0_0_a_0_0156_mm"),
            MatSusp0_0157_a_0_02      = json_data.get("MatSusp_0_0157_a_0_02_mm"),
            MatSusp0_0201_a_0_0625    = json_data.get("MatSusp_0_0201_a_0_0625_mm"),
            MatSusp0_0626_a_0_1250    = json_data.get("MatSusp_0_0626_a_0_1250_mm"),
            MatSusp0_1251_a_0_25      = json_data.get("MatSusp_0_1251_a_0_25_mm"),
            MatSusp0_2501_a_0_5       = json_data.get("MatSusp_0_2501_a_0_5_mm"),
            MatSusp0_501_a_1_0        = json_data.get("MatSusp_0_501_a_1_0_mm"),
            MatSusp1_0001_a_2_0       = json_data.get("MatSusp_1_0001_a_2_0_mm"),
            MatSusp2_0001_a_4_0       = json_data.get("MatSusp_2_0001_a_4_0_mm"),
            MatSusp4_0001_a_8_0       = json_data.get("MatSusp_4_0001_a_8_0_mm"),
            MatSusp8_0001_a_16_000    = json_data.get("MatSusp_8_0001_a_16_000_mm"),
            MatSuspD10                = json_data.get("MatSusp_D10_mm"),
            MatSuspD16                = json_data.get("MatSusp_D16_mm"),
            MatSuspD35                = json_data.get("MatSusp_D35_mm"),
            MatSuspD50                = json_data.get("MatSusp_D50_mm"),
            MatSuspD65                = json_data.get("MatSusp_D65_mm"),
            MatSuspD84                = json_data.get("MatSusp_D84_mm"),
            MatSuspD90                = json_data.get("MatSusp_D90_mm"),
            DataAlt                   = json_data.get("Data_Ultima_Alteracao")
        )


class CrossSection(HidroBase):
    """ Database model for storing Cross Section data. """

    __tablename__ = 'PerfilTransversal'

    RegistroID        = Column(Float, primary_key=True)

    EstacaoCodigo     = Column(BigInteger)
    """int: station code indifier of the registrie."""

    NivelConsistencia = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    Data              = Column(DateTime)
    """ datetime: date of measurements. """

    NumLevantamento   = Column(BigInteger)

    TipoSecao         = Column(SmallInteger)

    NumVerticais      = Column(BigInteger)

    DistanciaPIPF     = Column(Float)

    EixoXDistMaxima   = Column(Float)

    EixoXDistMinima   = Column(Float)

    EixoYCotaMaxima   = Column(Float)

    EixoYCotaMinima   = Column(Float)

    ElmGeomPassoCota  = Column(Float)

    Observacoes       = Column(String)


    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            RegistroID        = json_data.get("Registro_ID"),
            EstacaoCodigo     = json_data.get("codigoestacao"),
            NivelConsistencia = json_data.get("Nivel_Consistencia"),
            Data              = json_data.get("Data_Hora_Medicao"),
            NumLevantamento   = json_data.get("Num_Levantamento"),
            TipoSecao         = json_data.get("Tipo_Secao"),
            NumVerticais      = json_data.get("Num_Verticais"),
            DistanciaPIPF     = json_data.get("Distancia_pipf"),
            EixoXDistMaxima   = json_data.get("Eixo_X_Dist_Maxima"),
            EixoXDistMinima   = json_data.get("Eixo_X_Dist_Minima"),
            EixoYCotaMaxima   = json_data.get("Eixo_Y_Cota_Maxima"),
            EixoYCotaMinima   = json_data.get("Eixo_Y_Cota_Minima"),
            ElmGeomPassoCota  = json_data.get("Elm_Geom_Passo_Cota"),
            Observacoes       = json_data.get("Observacoes")
        )


class VerticalCrossSection(HidroBaseModel):
    """ Database model for storing Vertical Cross Section data. """

    __tablename__ = 'PerfilTransversalVert'

    PerfilTransversalID = Column(Float, ForeignKey("PerfilTransversal.RegistroID"), nullable=False)

    Cota                = Column(Float)

    Distancia           = Column(Float)


    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            PerfilTransversalID = json_data.get("Registro_ID"),
            Cota                = json_data.get("Cota"),
            Distancia           = json_data.get("Distancia")
        )


class FlowRate(HidroBaseModel):
    """ Database model for storing Flow Rate data. """

    __tablename__ = 'Vazoes'
    __table_args__ = (
        UniqueConstraint(
            'EstacaoCodigo',
            'Data',
            name='uq_flow_rate'
        ),
    )

    EstacaoCodigo        = Column(BigInteger)
    """int: station code indifier of the registrie."""

    NivelConsistencia    = Column(SmallInteger)
    """
    int: indicate the consistency of the registrie.
    0 - Brute.
    1 - Consisted.
    """

    Data                 = Column(DateTime)
    """ datetime: date of measurements. """
    
    MediaDiaria          = Column(SmallInteger)

    MetodoObtencaoVazoes = Column(SmallInteger)

    Maxima               = Column(Float)

    Minima               = Column(Float)

    Media                = Column(Float)

    DiaMaxima            = Column(SmallInteger)

    DiaMinima            = Column(SmallInteger)

    MaximaStatus         = Column(SmallInteger)

    MinimaStatus         = Column(SmallInteger)

    MediaStatus          = Column(SmallInteger)

    MediaAnual           = Column(Float)

    MediaAnualStatus     = Column(SmallInteger)

    # Hora                 = Column(DateTime)


    for i in range(1, 32):
        locals()[f'Vazao{i:02d}'] = Column(f'Vazao{i:02d}', Float)
        locals()[f'Vazao{i:02d}Status'] = Column(f'Vazao{i:02d}Status', SmallInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {
            "EstacaoCodigo":        json_data.get("codigoestacao"),
            "NivelConsistencia":    json_data.get("Nivel_Consistencia"),
            "Data":                 json_data.get("Data_Hora_Dado"),
            "MediaDiaria":          json_data.get("Mediadiaria"),
            "MetodoObtencaoVazoes": json_data.get("Metodo_Obtencao_Vazoes"),
            "Maxima":               json_data.get("Maxima"),
            "Minima":               json_data.get("Minima"),
            "Media":                json_data.get("Media"),
            "DiaMaxima":            json_data.get("Dia_Maxima"),
            "DiaMinima":            json_data.get("Dia_Minima"),
            "MaximaStatus":         json_data.get("Maxima_Status"),
            "MinimaStatus":         json_data.get("Minima_Status"),
            "MediaStatus":          json_data.get("Media_Status"),
            "MediaAnual":           json_data.get("Media_Anual"),
            "MediaAnualStatus":     json_data.get("Media_Anual_Status"),
            "DataAlt":              json_data.get("Data_Ultima_Alteracao"),
            # "Hora":               json_data.get("?"),
        }
        for i in range(1, 32):
            kwargs[f'Vazao{i:02d}']       = json_data.get(f"Vazao_{i:02d}")
            kwargs[f'Vazao{i:02d}Status'] = json_data.get(f"Vazao_{i:02d}_Status")
        return cls(**kwargs)
