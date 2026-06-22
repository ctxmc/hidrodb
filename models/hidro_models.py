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

from sqlalchemy import Column, Float, SmallInteger, BigInteger, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime

def str_to_datetime(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    else:
        return None

HidroBase = declarative_base()
class HidroBaseModel(HidroBase):
    __abstract__ = True

    RegistroID        = Column(Float, primary_key=True)
    Importado         = Column(SmallInteger, default=0)
    Temporario        = Column(SmallInteger, default=0)
    Removido          = Column(SmallInteger, default=0)
    ImportadoRepetido = Column(SmallInteger, default=0)
    DataIns           = Column(DateTime, default=func.now())

    def __init__(self, **kwargs):
        kwargs.setdefault('Importado',         0)
        kwargs.setdefault('Temporario',        0)
        kwargs.setdefault('Removido',          0)
        kwargs.setdefault('ImportadoRepetido', 0)
        super().__init__(**kwargs)

class Basin(HidroBaseModel):
    __tablename__ = 'Bacia'

    Nome    = Column(String)
    Codigo  = Column(Integer, unique=True)
    DataAlt = Column(DateTime)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome    = json_data.get("Nome_Bacia"),
            Codigo  = json_data.get("codigobacia"),
            DataAlt = str_to_datetime(json_data.get("Data_Ultima_Alteracao"))
        )

class SubBasin(HidroBaseModel):
    __tablename__ = 'SubBacia'

    Nome        = Column(String)
    Codigo      = Column(Integer, unique=True)
    BaciaCodigo = Column(Integer)
    DataAlt     = Column(DateTime)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome        = json_data.get("Sub_Bacia_Nome"),
            Codigo      = json_data.get("codigosubbacia"),
            DataAlt     = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
            BaciaCodigo = json_data.get("Bacia_Codigo")
        )


class Entity(HidroBaseModel):
    __tablename__ = 'Entidade'

    Nome    = Column(String)
    Sigla   = Column(String)
    Codigo  = Column(Integer, unique=True)
    DataAlt = Column(DateTime)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome    = json_data.get("Entidade_Nome"),
            Sigla   = json_data.get("Entidade_Sigla"),
            Codigo  = json_data.get("codigoentidade"),
            DataAlt = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
        )


class Township(HidroBaseModel):
    __tablename__ = 'Municipio'

    Nome       = Column(String)
    Codigo     = Column(Integer, unique=True)
    CodigoIBGE = Column(Integer)
    DataAlt    = Column(DateTime)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome       = json_data.get("Municipio_Nome"),
            Codigo     = json_data.get("codigomunicipio"),
            CodigoIBGE = json_data.get("Municipio_Codigo_IBGE"),
            DataAlt    = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
        )


class River(HidroBaseModel):
    __tablename__ = 'Rio'

    Nome              = Column(String)
    Codigo            = Column(Integer, unique=True)
    DataAlt           = Column(DateTime)
    Jurisdicao        = Column(SmallInteger)
    BaciaCodigo       = Column(Integer)
    SubBaciaCodigo    = Column(Integer)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome           = json_data.get("Nome_Rio"),
            Codigo         = json_data.get("codigorio"),
            DataAlt        = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
            Jurisdicao     = json_data.get("Rio_Jurisdicao"),
            BaciaCodigo    = json_data.get("Bacia_Codigo"),
            SubBaciaCodigo = json_data.get("Sub_Bacia_Codigo"),
        )


class State(HidroBaseModel):
    __tablename__ = 'Estado'

    Nome       = Column(String)
    Sigla      = Column(String)
    Codigo     = Column(Integer, unique=True)
    DataAlt    = Column(DateTime)
    CodigoIBGE = Column(Integer)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Nome       = json_data.get("Estado_Nome"),
            Sigla      = json_data.get("Estado_Sigla"),
            Codigo     = json_data.get("codigouf"),
            CodigoIBGE = json_data.get("Estado_Codigo_IBGE"),
            DataAlt    = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
        )


class Station(HidroBaseModel):
    __tablename__ = 'Estacao'

    Altitude                      = Column(Float)
    AreaDrenagem                  = Column(Float)
    CodigoAdicional               = Column(String(15))
    OperadoraUnidade              = Column(Integer)
    PeriodoClimatologicaFim       = Column(DateTime)
    PeriodoClimatologicaInicio    = Column(DateTime)
    PeriodoEscalaFim              = Column(DateTime)
    PeriodoEscalaInicio           = Column(DateTime)
    PeriodoPiezometriaFim         = Column(DateTime)
    PeriodoPiezometriaInicio      = Column(DateTime)
    PeriodoPluviometroFim         = Column(DateTime)
    PeriodoPluviometroInicio      = Column(DateTime)
    PeriodoQualAguaFim            = Column(DateTime)
    PeriodoQualAguaInicio         = Column(DateTime)
    PeriodoRegistradorChuvaFim    = Column(DateTime)
    PeriodoRegistradorChuvaInicio = Column(DateTime)
    PeriodoRegistradorNivelFim    = Column(DateTime)
    PeriodoRegistradorNivelInicio = Column(DateTime)
    PeriodoSedimentosFim          = Column(DateTime)
    PeriodoSedimentosInicio       = Column(DateTime)
    PeriodoTanqueEvapoFim         = Column(DateTime)
    PeriodoTanqueEvapoInicio      = Column(DateTime)
    PeriodoTelemetricaFim         = Column(DateTime)
    PeriodoTelemetricaInicio      = Column(DateTime)
    UltimaAtualizacao             = Column(DateTime)
    Nome                          = Column(String(50))
    Latitude                      = Column(Float)
    Longitude                     = Column(Float)
    MunicipioCodigo               = Column(Integer)
    EstadoCodigo                  = Column(Integer)
    OperadoraCodigo               = Column(BigInteger)
    OperadoraSubUnidade           = Column(Integer)
    Operando                      = Column(SmallInteger)
    ResponsavelCodigo             = Column(BigInteger)
    ResponsavelUnidade            = Column(Integer)
    RioCodigo                     = Column(BigInteger)
    SubBaciaCodigo                = Column(BigInteger)
    TipoEstacaoClimatologica      = Column(SmallInteger)
    TipoEstacaoDescLiquida        = Column(SmallInteger)
    PeriodoDescLiquidaFim         = Column(SmallInteger)
    PeriodoDescLiquidaInicio      = Column(SmallInteger)
    # TipoEstacao                 = Column(SmallInteger) # TODO
    TipoEstacaoEscala             = Column(SmallInteger)
    TipoEstacaoPiezometria        = Column(SmallInteger)
    TipoEstacaoPluviometro        = Column(SmallInteger)
    TipoEstacaoQualAgua           = Column(SmallInteger)
    TipoEstacaoRegistradorChuva   = Column(SmallInteger)
    TipoEstacaoRegistradorNivel   = Column(SmallInteger)
    TipoEstacaoSedimentos         = Column(SmallInteger)
    TipoEstacaoTanqueEvapo        = Column(SmallInteger)
    TipoEstacaoTelemetrica        = Column(SmallInteger)
    TipoRedeBasica                = Column(SmallInteger)
    TipoRedeCaptacao              = Column(SmallInteger)
    TipoRedeClasseVazao           = Column(SmallInteger)
    TipoRedeCursoDagua            = Column(SmallInteger)
    TipoRedeEnergetica            = Column(SmallInteger)
    TipoRedeEstrategica           = Column(SmallInteger)
    TipoRedeNavegacao             = Column(SmallInteger)
    TipoRedeQualAgua              = Column(SmallInteger)
    TipoRedeSedimentos            = Column(SmallInteger)
    BaciaCodigo                   = Column(BigInteger)
    Codigo                        = Column(BigInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            Altitude                      = json_data.get("Altitude"),
            AreaDrenagem                  = json_data.get("Area_Drenagem"),
            CodigoAdicional               = json_data.get("Codigo_Adicional"),
            OperadoraUnidade              = json_data.get("Codigo_Operadora_Unidade_UF"),
            PeriodoClimatologicaFim       = str_to_datetime(json_data.get("Data_Periodo_Climatologica_Fim")),
            PeriodoClimatologicaInicio    = str_to_datetime(json_data.get("Data_Periodo_Climatologica_Inicio")),
            PeriodoDescLiquidaFim         = str_to_datetime(json_data.get("Data_Periodo_Desc_Liquida_Fim")),
            PeriodoDescLiquidaInicio      = str_to_datetime(json_data.get("Data_Periodo_Desc_liquida_Inicio")),
            PeriodoEscalaFim              = str_to_datetime(json_data.get("Data_Periodo_Escala_Fim")),
            PeriodoEscalaInicio           = str_to_datetime(json_data.get("Data_Periodo_Escala_Inicio")),
            PeriodoPiezometriaFim         = str_to_datetime(json_data.get("Data_Periodo_Piezometria_Fim")),
            PeriodoPiezometriaInicio      = str_to_datetime(json_data.get("Data_Periodo_Piezometria_Inicio")),
            PeriodoPluviometroFim         = str_to_datetime(json_data.get("Data_Periodo_Pluviometro_Fim")),
            PeriodoPluviometroInicio      = str_to_datetime(json_data.get("Data_Periodo_Pluviometro_Inicio")),
            PeriodoQualAguaFim            = str_to_datetime(json_data.get("Data_Periodo_Qual_Agua_Fim")),
            PeriodoQualAguaInicio         = str_to_datetime(json_data.get("Data_Periodo_Qual_Agua_Inicio")),
            PeriodoRegistradorChuvaFim    = str_to_datetime(json_data.get("Data_Periodo_Registrador_Chuva_Fim")),
            PeriodoRegistradorChuvaInicio = str_to_datetime(json_data.get("Data_Periodo_Registrador_Chuva_Inicio")),
            PeriodoRegistradorNivelFim    = str_to_datetime(json_data.get("Data_Periodo_Registrador_Nivel_Fim")),
            PeriodoRegistradorNivelInicio = str_to_datetime(json_data.get("Data_Periodo_Registrador_Nivel_Inicio")),
            PeriodoSedimentosFim          = str_to_datetime(json_data.get("Data_Periodo_Sedimento_Fim")),
            PeriodoSedimentosInicio       = str_to_datetime(json_data.get("Data_Periodo_Sedimento_Inicio")),
            PeriodoTanqueEvapoFim         = str_to_datetime(json_data.get("Data_Periodo_Tanque_Evapo_Fim")),
            PeriodoTanqueEvapoInicio      = str_to_datetime(json_data.get("Data_Periodo_Tanque_Evapo_Inicio")),
            PeriodoTelemetricaFim         = str_to_datetime(json_data.get("Data_Periodo_Telemetrica_Fim")),
            PeriodoTelemetricaInicio      = str_to_datetime(json_data.get("Data_Periodo_Telemetrica_Inicio")),
            UltimaAtualizacao             = str_to_datetime(json_data.get("Data_Ultima_Atualizacao")),
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
            # TipoEstacao                 = json.get("Tipo_Estacao"), # TODO
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
    __tablename__ = 'Chuvas'

    Data                 = Column(DateTime)
    DataAlt              = Column(DateTime)
    DiaMaxima            = Column(SmallInteger)
    Maxima               = Column(Float)
    MaximaStatus         = Column(SmallInteger)
    NivelConsistencia    = Column(SmallInteger)
    NumDiasDeChuva       = Column(SmallInteger)
    NumDiasDeChuvaStatus = Column(SmallInteger)
    TipoMedicaoChuvas    = Column(SmallInteger)
    Total                = Column(Float)
    TotalAnual           = Column(Float)
    TotalAnualStatus     = Column(SmallInteger)
    TotalStatus          = Column(SmallInteger)
    EstacaoCodigo        = Column(BigInteger)

    locals().update({
        f'Chuva{i:02d}': Column(f'Chuva{i:02d}', Float)
        for i in range(1, 32)
    })
    locals().update({
        f'Chuva{i:02d}Status': Column(f'Chuva{i:02d}Status', SmallInteger)
        for i in range(1, 32)
    })

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {
            'Data':                 str_to_datetime(json_data.get("Data_Hora_Dado")),
            'DataAlt':              str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
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
    __tablename__ = 'ResumoDescarga'

    AreaMolhada       = Column(Float)
    Cota              = Column(Float)
    Data              = Column(DateTime)
    DataAlt           = Column(DateTime)
    Largura           = Column(Float)
    NivelConsistencia = Column(SmallInteger)
    Profundidade      = Column(Float)
    Vazao             = Column(Float)
    VelMedia          = Column(Float)
    EstacaoCodigo     = Column(BigInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            AreaMolhada       = json_data.get("Area_Molhada"),
            Cota              = json_data.get("Cota (cm)"),
            Data              = str_to_datetime(json_data.get("Data_Hora_Dado")),
            DataAlt           = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
            Largura           = json_data.get("Largura (m)"),
            NivelConsistencia = json_data.get("Nivel_Consistencia"),
            Profundidade      = json_data.get("Profundidade (m)"),
            Vazao             = json_data.get("Vazao (m3/s)"),
            VelMedia          = json_data.get("Vel_Media (m/s)"),
            EstacaoCodigo     = json_data.get("codigoestacao"),
        )


class Sediments(HidroBaseModel):
    __tablename__ = 'Sedimentos'

    AreaMolhada                = Column(Float)
    ConcentracaoMatSuspensao   = Column(Float)
    ConcentracaoDaAmostraExtra = Column(Float)
    CondutividadeEletrica      = Column(Float)
    Cota                       = Column(Float)
    CotaDeMedicao              = Column(Float)
    Data                       = Column(DateTime)
    DataLiq                    = Column(DateTime)
    DataAlt                    = Column(DateTime)
    Largura                    = Column(Float)
    NivelConsistencia          = Column(SmallInteger)
    NumMedicao                 = Column(BigInteger)
    NumMedicaoLiq              = Column(BigInteger)
    Observacoes                = Column(String)
    TemperaturaDaAgua          = Column(Float)
    Vazao                      = Column(Float)
    Velmedia                   = Column(Float)
    EstacaoCodigo              = Column(BigInteger)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            AreaMolhada                = json_data.get("Area_Molhada"),
            ConcentracaoMatSuspensao   = json_data.get("Concentracao_PPM"),
            ConcentracaoDaAmostraExtra = json_data.get("Concentracao_da_Amostra_Extra"),
            CondutividadeEletrica      = json_data.get("Condutividade_Eletrica"),
            Cota                       = json_data.get("Cota_cm"),
            CotaDeMedicao              = json_data.get("Cota_de_Mediacao"),
            Data                       = str_to_datetime(json_data.get("Data_Hora_Dado")),
            DataLiq                    = str_to_datetime(json_data.get("Data_Hora_Medicao_Liquida")),
            DataAlt                    = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
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
    __tablename__ = 'Cotas'

    Data              = Column(DateTime)
    DataAlt           = Column(DateTime)
    DiaMaxima         = Column(SmallInteger)
    DiaMinima         = Column(SmallInteger)
    Maxima            = Column(Float)
    MaximaStatus      = Column(SmallInteger)
    Media             = Column(Float)
    MediaAnual        = Column(Float)
    MediaAnualStatus  = Column(SmallInteger)
    MediaStatus       = Column(SmallInteger)
    MediaDiaria       = Column(SmallInteger)
    Minima            = Column(Float)
    MinimaStatus      = Column(SmallInteger)
    TipoMedicaoCotas  = Column(SmallInteger)
    EstacaoCodigo     = Column(BigInteger)
    NivelConsistencia = Column(SmallInteger)

    locals().update({
        f'Cota{i:02d}': Column(f'Cota{i:02d}', Float)
        for i in range(1, 32)
    })
    locals().update({
        f'Cota{i:02d}Status': Column(f'Cota{i:02d}Status', SmallInteger)
        for i in range(1, 32)
    })

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {
            "Data":              str_to_datetime(json_data.get("Data_Hora_Dado")),
            "DataAlt":           str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
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
    __tablename__ = 'CurvaDescarga'

    CoefA                 = Column(Float)
    CoefH0                = Column(Float)
    CoefN                 = Column(Float)
    CoefA0                = Column(Float)
    CoefA1                = Column(Float)
    CoefA2                = Column(Float)
    CoefA3                = Column(Float)
    CotaMaxima            = Column(Float)
    CotaMinima            = Column(Float)
    DataAlt               = Column(DateTime)
    NivelConsistencia     = Column(SmallInteger)
    NumeroCurva           = Column(String(5))
    PeriodoValidadeFim    = Column(DateTime)
    PeriodoValidadeInicio = Column(DateTime)
    TabelaPassoCota       = Column(Float)
    TipoCurva             = Column(SmallInteger)
    TipoEquacao           = Column(SmallInteger)
    EstacaoCodigo         = Column(BigInteger)

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
            DataAlt               = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
            NivelConsistencia     = json_data.get("Nivel_Consistencia"),
            NumeroCurva           = json_data.get("Numero_Curva"),
            PeriodoValidadeFim    = str_to_datetime(json_data.get("Periodo_Validade_Fim")),
            PeriodoValidadeInicio = str_to_datetime(json_data.get("Periodo_Validade_Inicio")),
            TabelaPassoCota       = json_data.get("Tabela_Passo_Cota"),
            TipoCurva             = json_data.get("Tipo_Curva"),
            TipoEquacao           = json_data.get("Tipo_Equacao"),
            EstacaoCodigo         = json_data.get("codigoestacao")
        )


class WaterQuality(HidroBaseModel):
    __tablename__ = 'QualAgua'

    n245T                       = Column(Float)
    n245TP                      = Column(Float)
    n246Triclorofenol           = Column(Float)
    Acido24Diclorofenoxiacetico = Column(Float)
    Aldrin                      = Column(Float)
    AzinfosEtil                 = Column(Float)
    Benzeno                     = Column(Float)
    BenzoAPireno                = Column(Float)
    BHC                         = Column(Float)
    BifenilasPolicloradas       = Column(Float)
    Escherichia                 = Column(Float)
    Carbaril                    = Column(Float)
    Clordano                    = Column(Float)
    DDEPP                       = Column(Float)
    DDT                         = Column(Float)
    Demeton                     = Column(Float)
    Diazinon                    = Column(Float)
    Dieldrin                    = Column(Float)
    DodecacloroNonacloro        = Column(Float)
    DySystonDisulfton           = Column(Float)
    Endossulfan                 = Column(Float)
    FitoplanctonQuantitativo    = Column(Float)
    Endrin                      = Column(Float)
    EpoxidoHeptacloro           = Column(Float)
    Ethion                      = Column(Float)
    Gution                      = Column(Float)
    Heptacloro                  = Column(Float)
    Lindano                     = Column(Float)
    Malation                    = Column(Float)
    MetilParation               = Column(Float)
    Metoxicloro                 = Column(Float)
    Paration                    = Column(Float)
    FosforoTotal                = Column(Float)
    Pentaclorofenol             = Column(Float)
    Phosdrin                    = Column(Float)
    TetracloretoCarbono         = Column(Float)
    Tetracloroeteno             = Column(Float)
    Toxafeno                    = Column(Float)
    Tricloroeteno               = Column(Float)
    Algas                       = Column(Float)
    Amoniaco                    = Column(Float)
    BacteriasHeterotroficas     = Column(Float)
    CloroResidual               = Column(Float)
    Nitratos                    = Column(Float)
    Colifagos                   = Column(Float)
    ContagemBacteriasPlaca      = Column(Float)
    EnteroBacteriasPatogenicas  = Column(Float)
    Fungos                      = Column(Float)
    NitrogenioAlbuminoide       = Column(Float)
    Protozoarios                = Column(Float)
    Salmonelas                  = Column(Float)
    ZooplanctonTotal            = Column(Float)
    NitrogenioAmoniacal         = Column(Float)
    NitrogenioTotal             = Column(Float)
    OrtofosfatoTotal            = Column(Float)
    OD                          = Column(Float)
    pH                          = Column(Float)
    SolDissolvidosTotais        = Column(Float)
    AlcalinidadeTotal           = Column(Float)
    SolSuspensaoTotais          = Column(Float)
    TempAmostra                 = Column(Float)
    TempAr                      = Column(Float)
    Transparencia               = Column(Float)
    Turbidez                    = Column(Float)
    Acidez                      = Column(Float)
    AlcalinidadeCO3             = Column(Float)
    AlcalinidadeHCO3            = Column(Float)
    AlcalinidadeOH              = Column(Float)
    Aluminiodissolvido          = Column(Float)
    CarbonoOrganicoTotal        = Column(Float)
    Aluminio                    = Column(Float)
    AmoniaNaoIonizavel          = Column(Float)
    Arsenio                     = Column(Float)
    Bario                       = Column(Float)
    Berilio                     = Column(Float)
    BismutoTotal                = Column(Float)
    Borodissolvido              = Column(Float)
    Boro                        = Column(Float)
    Cadmio                      = Column(Float)
    CalcioTotal                 = Column(Float)
    Cloretos                    = Column(Float)
    Chumbo                      = Column(Float)
    Cianetolivre                = Column(Float)
    Cianetos                    = Column(Float)
    Cobalto                     = Column(Float)
    Cobredissolvido             = Column(Float)
    Cobre                       = Column(Float)
    ColiformesFecais            = Column(Float)
    ColiformesTotais            = Column(Float)
    CompostosOrganoclorados     = Column(Float)
    CompostosOrganofosforados   = Column(Float)
    CondutividadeEletrica       = Column(Float)
    Cor                         = Column(Float)
    CromoHexavalente            = Column(Float)
    CromoTotal                  = Column(Float)
    CromoTrivalente             = Column(Float)
    Densidadecianobacterias     = Column(Float)
    Detergentes                 = Column(Float)
    Dureza                      = Column(Float)
    Durezamagnesio              = Column(Float)
    DurezaTotal                 = Column(Float)
    ColiformesTermotolerantes   = Column(Float)
    EstreptococosFecais         = Column(Float)
    FerroDissolvido             = Column(Float)
    FerroTotal                  = Column(Float)
    Fluoretos                   = Column(Float)
    FosfatoTotal                = Column(Float)
    Hidrocarbonetos             = Column(Float)
    IndiceFenois                = Column(Float)
    IQA                         = Column(Float)
    Litio                       = Column(Float)
    CondutividadeEspecifica     = Column(Float)
    MagnesioTotal               = Column(Float)
    Manganes                    = Column(Float)
    Mercurio                    = Column(Float)
    Niquel                      = Column(Float)
    Nitritos                    = Column(Float)
    NitrogenioOrganico          = Column(Float)
    NitrogenioTotalKJELDAHL     = Column(Float)
    OleosGraxas                 = Column(Float)
    ODsaturacao                 = Column(Float)
    PotassioTotal               = Column(Float)
    DBO                         = Column(Float)
    Prata                       = Column(Float)
    ParametroProfundidade       = Column(Float)
    Selenio                     = Column(Float)
    SilicaDissolvida            = Column(Float)
    SodioTotal                  = Column(Float)
    SolDissolvidosFixos         = Column(Float)
    SolDissolvidosVolateis      = Column(Float)
    SolSuspensaoFixos           = Column(Float)
    SolSuspensaoVolateis        = Column(Float)
    SolFixos                    = Column(Float)
    DescargaLiquida             = Column(Float)
    SolSedimentaveis            = Column(Float)
    SolTotais                   = Column(Float)
    SolVolateis                 = Column(Float)
    Sulfatos                    = Column(Float)
    Sulfetos                    = Column(Float)
    UranioTotal                 = Column(Float)
    Vanadio                     = Column(Float)
    Zinco                       = Column(Float)
    n11Dicloroeteno             = Column(Float)
    n12Dicloroetano             = Column(Float)
    DQO                         = Column(Float)
    Choveu                      = Column(SmallInteger)
    Data                        = Column(DateTime)
    DataAlt                     = Column(DateTime)
    NivelConsistencia           = Column(SmallInteger)
    NumMedicao                  = Column(BigInteger)
    PosHorizColeta              = Column(SmallInteger)
    PosVertColeta               = Column(SmallInteger)
    Profundidade                = Column(Float)
    EstacaoCodigo               = Column(BigInteger)

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
            Data                        = str_to_datetime(json_data.get("Data_Hora_Dado")),
            DataAlt                     = str_to_datetime(json_data.get("Data_Ultima_Alteracao")),
            NivelConsistencia           = json_data.get("Nilvel_ConsistÃªncia"),
            NumMedicao                  = json_data.get("Num_Medicao"),
            PosHorizColeta              = json_data.get("Posicao_Horizontal_Coleta"),
            PosVertColeta               = json_data.get("Posicao_Vertical_Coleta"),
            Profundidade                = json_data.get("Profundidade_m"),
            EstacaoCodigo               = json_data.get("codigoestacao")
        )


class WaterQualityStatus(HidroBase):
    __tablename__ = 'QualAguaStatus'

    RegistroID = Column(Float, primary_key=True)
    Removido   = Column(SmallInteger, default=0)
    locals().update({
        f'QualAgua{i:03d}Status': Column(f'QualAgua{i:03d}Status', SmallInteger)
        for i in range(1, 148)
    })

    @classmethod
    def from_json(cls, json_data: dict):
        kwargs = {}
        for i in range(1, 148):
            kwargs[f"QualAgua{i:03d}Status"] = json_data.get(f"{i}_Status")

        return cls(**kwargs)


class Granulometry(HidroBaseModel):
    __tablename__ = 'Granulometria'

    EstacaoCodigo             = Column(BigInteger)
    NivelConsistencia         = Column(SmallInteger)
    # Data                      = Column(DateTime)
    # HoraInicial               = Column(DateTime)
    # HoraFinal                 = Column(DateTime)
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
    DataAlt                   = Column(DateTime)

    @classmethod
    def from_json(cls, json_data: dict):
        return cls(
            EstacaoCodigo             = json_data.get("codigoestacao"),
            NivelConsistencia         = json_data.get("Nivel_Consistencia"),
            # Data                      = json_data.get("Data_Dado"),
            # HoraInicial               = json_data.get("Hora_Final"),
            # HoraFinal                 = json_data.get("Hora_Inicial"),
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
            DataAlt                   = str_to_datetime(json_data.get("Data_Ultima_Alteracao"))
        )

class CrossSection(HidroBaseModel):
    __tablename__ = 'PerfilTransversal'

    EstacaoCodigo     = Column(BigInteger)
    NivelConsistencia = Column(SmallInteger)
    Data              = Column(DateTime)
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
            Data              = str_to_datetime(json_data.get("Data_Hora_Medicao")),
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


class VerticalCrossSection(HidroBase):
    __tablename__ = 'PerfilTransversalVert'

    RegistroID = Column(Float, primary_key=True)
    Removido   = Column(SmallInteger, default=0)
    Cota       = Column(Float)
    Distancia  = Column(Float)

    @classmethod
    def from_json(cls, json_data: dict, reg_id):
        return cls(
            RegistroID = reg_id,
            Removido   = 0,
            Cota       = json_data.get("Cota"),
            Distancia  = json_data.get("Distancia")
        )
