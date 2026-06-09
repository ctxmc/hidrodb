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

from typing import Dict
from datetime import datetime

class AccessEntrie():
    def __init__(self, reg_id: int, **kwargs):
        self.fields = {
            "RegistroID":        reg_id,
            "Importado":         0,
            "Temporario":        0,
            "Removido":          0,
            "ImportadoRepetido": 0,
            "DataIns":           datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.fields.update(kwargs)

    def keys(self) -> str:
        return ", ".join(self.fields.keys())

    def data(self) -> tuple:
        return tuple(self.fields.values())

    def values(self) -> str:
        return ','.join('?' for _ in self.keys().split(','))


class Basin:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":    json.get("Nome_Bacia"),
            "Codigo":  json.get("codigobacia"),
            "DataAlt": json.get("Data_Ultima_Alteracao")
        }


class SubBasin:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":        json.get("Sub_Bacia_Nome"),
            "Codigo":      json.get("codigosubbacia"),
            "DataAlt":     json.get("Data_Ultima_Alteracao"),
            "BaciaCodigo": json.get("Bacia_Codigo")
        }


class Entity:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":    json.get("Entidade_Nome"),
            "Sigla":   json.get("Entidade_Sigla"),
            "Codigo":  json.get("codigoentidade"),
            "DataAlt": json.get("Data_Ultima_Alteracao")
        }


class Township:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":         json.get("Municipio_Nome"),
            "Codigo":       json.get("codigomunicipio"),
            "DataAlt":      json.get("Data_Ultima_Alteracao"),
            "CodigoIBGE":   json.get("Municipio_Codigo_IBGE"),
            "EstadoCodigo": json.get("Estado_Codigo")
        }


class River:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":           json.get("Nome_Rio"),
            "Codigo":         json.get("codigorio"),
            "DataAlt":        json.get("Data_Ultima_Alteracao"),
            "Jurisdicao":     json.get("Rio_Jurisdicao"),
            "BaciaCodigo":    json.get("Bacia_Codigo"),
            "SubBaciaCodigo": json.get("Sub_Bacia_Codigo")
        }


class State:
    def __init__(self, json: dict):
        self.fields = {
            "Nome":           json.get("Estado_Nome"),
            "Sigla":          json.get("Estado_Sigla"),
            "Codigo":         json.get("codigouf"),
            "DataAlt":        json.get("Data_Ultima_Alteracao"),
            "CodigoIBGE":     json.get("Estado_Codigo_IBGE")
        }


class Station:
    def __init__(self, json: dict):
        self.fields = {
            "Altitude":                      json.get("Altitude"),
            "AreaDrenagem":                  json.get("Area_Drenagem"),
            # "?":                           json.get("Bacia_Nome"),
            "CodigoAdicional":               json.get("Codigo_Adicional"),
            "OperadoraUnidade":              json.get("Codigo_Operadora_Unidade_UF"),
            "PeriodoClimatologicaFim":       json.get("Data_Periodo_Climatologica_Fim"),
            "PeriodoClimatologicaInicio":    json.get("Data_Periodo_Climatologica_Inicio"),
            "PeriodoDescLiquidaFim":         json.get("Data_Periodo_Desc_Liquida_Fim"),
            "PeriodoDescLiquidaInicio":      json.get("Data_Periodo_Desc_liquida_Inicio"),
            "PeriodoEscalaFim":              json.get("Data_Periodo_Escala_Fim"),
            "PeriodoEscalaInicio":           json.get("Data_Periodo_Escala_Inicio"),
            "PeriodoPiezometriaFim":         json.get("Data_Periodo_Piezometria_Fim"),
            "PeriodoPiezometriaInicio":      json.get("Data_Periodo_Piezometria_Inicio"),
            "PeriodoPluviometroFim":         json.get("Data_Periodo_Pluviometro_Fim"),
            "PeriodoPluviometroInicio":      json.get("Data_Periodo_Pluviometro_Inicio"),
            "PeriodoQualAguaFim":            json.get("Data_Periodo_Qual_Agua_Fim"),
            "PeriodoQualAguaInicio":         json.get("Data_Periodo_Qual_Agua_Inicio"),
            "PeriodoRegistradorChuvaFim":    json.get("Data_Periodo_Registrador_Chuva_Fim"),
            "PeriodoRegistradorChuvaInicio": json.get("Data_Periodo_Registrador_Chuva_Inicio"),
            "PeriodoRegistradorNivelFim":    json.get("Data_Periodo_Registrador_Nivel_Fim"),
            "PeriodoRegistradorNivelInicio": json.get("Data_Periodo_Registrador_Nivel_Inicio"),
            "PeriodoSedimentosFim":          json.get("Data_Periodo_Sedimento_Fim"),
            "PeriodoSedimentosInicio":       json.get("Data_Periodo_Sedimento_Inicio"),
            "PeriodoTanqueEvapoFim":         json.get("Data_Periodo_Tanque_Evapo_Fim"),
            "PeriodoTanqueEvapoInicio":      json.get("Data_Periodo_Tanque_Evapo_Inicio"),
            "PeriodoTelemetricaFim":         json.get("Data_Periodo_Telemetrica_Fim"),
            "PeriodoTelemetricaInicio":      json.get("Data_Periodo_Telemetrica_Inicio"),
            "UltimaAtualizacao":             json.get("Data_Ultima_Atualizacao"),
            "Nome":                          json.get("Estacao_Nome"),
            "Latitude":                      json.get("Latitude"),
            "Longitude":                     json.get("Longitude"),
            "MunicipioCodigo":               json.get("Municipio_Codigo"),
            # "?":                           json.get("Municipio_Nome"),
            "OperadoraCodigo":               json.get("Operadora_Codigo"),
            # "?":                           json.get("Operadora_Sigla"),
            "OperadoraSubUnidade":           json.get("Operadora_Sub_Unidade_UF"),
            "Operando":                      json.get("Operando"),
            "ResponsavelCodigo":             json.get("Responsavel_Codigo"),
            "ResponsavelUnidade":            json.get("Responsavel_Unidade_UF"),
            "RioCodigo":                     json.get("Rio_Codigo"),
            # "?":                           json.get("Rio_Nome"),
            "SubBaciaCodigo":                json.get("Sub_Bacia_Codigo"),
            # "?":                           json.get("Sub_Bacia_Nome"),
            # "TipoEstacao":                 json.get("Tipo_Estacao"), # TODO
            "TipoEstacaoClimatologica":      json.get("Tipo_Estacao_Climatologica"),
            "TipoEstacaoDescLiquida":        json.get("Tipo_Estacao_Desc_Liquida"),
            "TipoEstacaoEscala":             json.get("Tipo_Estacao_Escala"),
            "TipoEstacaoPiezometria":        json.get("Tipo_Estacao_Piezometria"),
            "TipoEstacaoPluviometro":        json.get("Tipo_Estacao_Pluviometro"),
            "TipoEstacaoQualAgua":           json.get("Tipo_Estacao_Qual_Agua"),
            "TipoEstacaoRegistradorChuva":   json.get("Tipo_Estacao_Registrador_Chuva"),
            "TipoEstacaoRegistradorNivel":   json.get("Tipo_Estacao_Registrador_Nivel"),
            "TipoEstacaoSedimentos":         json.get("Tipo_Estacao_Sedimentos"),
            "TipoEstacaoTanqueEvapo":        json.get("Tipo_Estacao_Tanque_evapo"),
            "TipoEstacaoTelemetrica":        json.get("Tipo_Estacao_Telemetrica"),
            "TipoRedeBasica":                json.get("Tipo_Rede_Basica"),
            "TipoRedeCaptacao":              json.get("Tipo_Rede_Captacao"),
            "TipoRedeClasseVazao":           json.get("Tipo_Rede_Classe_Vazao"),
            "TipoRedeCursoDagua":            json.get("Tipo_Rede_Curso_Dagua"),
            "TipoRedeEnergetica":            json.get("Tipo_Rede_Energetica"),
            "TipoRedeEstrategica":           json.get("Tipo_Rede_Estrategica"),
            "TipoRedeNavegacao":             json.get("Tipo_Rede_Navegacao"),
            "TipoRedeQualAgua":              json.get("Tipo_Rede_Qual_Agua"),
            "TipoRedeSedimentos":            json.get("Tipo_Rede_Sedimentos"),
            # "?":                           json.get("UF_Estacao"),
            # "?":                           json.get("UF_Nome_Estacao"),
            "BaciaCodigo":                   json.get("codigobacia"),
            "Codigo":                        json.get("codigoestacao")
        }


class Rain:
    def __init__(self, json: dict):
        self.fields = {
            "Data":                 json.get("Data_Hora_Dado"),
            "DataAlt":              json.get("Data_Ultima_Alteracao"),
            "DiaMaxima":            json.get("Dia_Maxima"),
            "Maxima":               json.get("Maxima"),
            "MaximaStatus":         json.get("Maxima_Status"),
            "NivelConsistencia":    json.get("Nivel_Consistencia"),
            "NumDiasDeChuva":       json.get("Numero_Dias_de_Chuva"),
            "NumDiasDeChuvaStatus": json.get("Numero_Dias_de_Chuva_Status"),
            "TipoMedicaoChuvas":    json.get("Tipo_Medicao_Chuvas"),
            "Total":                json.get("Total"),
            "TotalAnual":           json.get("Total_Anual"),
            "TotalAnualStatus":     json.get("Total_Anual_Status"),
            "TotalStatus":          json.get("Total_Status"),
            "EstacaoCodigo":        json.get("codigoestacao")
        }
        for i in range(1, 32):
            self.fields[f"Chuva{i:02d}"]       = json.get(f"Chuva_{i:02d}")
            self.fields[f"Chuva{i:02d}Status"] = json.get(f"Chuva_{i:02d}_Status")


class DischargeSummary:
    def __init__(self, json: dict):
        self.fields = {
            "AreaMolhada":       json.get("Area_Molhada"),
            "Cota":              json.get("Cota (cm)"),
            "Data":              json.get("Data_Hora_Dado"),
            "DataAlt":           json.get("Data_Ultima_Alteracao"),
            "Largura":           json.get("Largura (m)"),
            "NivelConsistencia": json.get("Nivel_Consistencia"),
            "Profundidade":      json.get("Profundidade (m)"),
            "Vazao":             json.get("Vazao (m3/s)"),
            "VelMedia":          json.get("Vel_Media (m/s)"),
            "EstacaoCodigo":     json.get("codigoestacao")
        }


class Sediments:
    def __init__(self, json: dict):
        self.fields = {
            "AreaMolhada":                json.get("Area_Molhada"),
            "ConcentracaoMatSuspensao":   json.get("Concentracao_PPM"),
            "ConcentracaoDaAmostraExtra": json.get("Concentracao_da_Amostra_Extra"),
            "CondutividadeEletrica":      json.get("Condutividade_Eletrica"),
            "Cota":                       json.get("Cota_cm"),
            "CotaDeMedicao":              json.get("Cota_de_Mediacao"),
            "Data":                       json.get("Data_Hora_Dado"),
            "DataLiq":                    json.get("Data_Hora_Medicao_Liquida"),
            "DataAlt":                    json.get("Data_Ultima_Alteracao"),
            "Largura":                    json.get("Largura"),
            "NivelConsistencia":          json.get("Nivel_Consistencia"),
            "NumMedicao":                 json.get("Numero_Medicao"),
            "NumMedicaoLiq":              json.get("Numero_Medicao_Liquida"),
            "Observacoes":                json.get("Observacoes"),
            "TemperaturaDaAgua":          json.get("Temperatura_da_Agua"),
            "Vazao":                      json.get("Vazao_m3_s"),
            "Velmedia":                   json.get("Vel_Media"),
            "EstacaoCodigo":              json.get("codigoestacao")
        }


class Stage:
    def __init__(self, json: dict):
        self.fields = {
            "Data":              json.get("Data_Hora_Dado"),
            "DataAlt":           json.get("Data_Ultima_Alteracao"),
            "DiaMaxima":         json.get("Dia_Maxima"),
            "DiaMinima":         json.get("Dia_Minima"),
            "Maxima":            json.get("Maxima"),
            "MaximaStatus":      json.get("Maxima_Status"),
            "Media":             json.get("Media"),
            "MediaAnual":        json.get("Media_Anual"),
            "MediaAnualStatus":  json.get("Media_Anual_Status"),
            "MediaStatus":       json.get("Media_Status"),
            "MediaDiaria":       json.get("Mediadiaria"),
            "Minima":            json.get("Minima"),
            "MinimaStatus":      json.get("Minima_Status"),
            "TipoMedicaoCotas":  json.get("Tipo_Medicao_Cotas"),
            "EstacaoCodigo":     json.get("codigoestacao"),
            "NivelConsistencia": json.get("nivelconsistencia")
        }
        for i in range(1, 32):
            self.fields[f"Cota{i:02d}"]       = json.get(f"Cota_{i:02d}")
            self.fields[f"Cota{i:02d}Status"] = json.get(f"Cota_{i:02d}_Status")
