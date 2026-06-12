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

    @classmethod
    def with_id(cls, **kwargs):
        instance = cls.__new__(cls)
        instance.fields = {
            "Importado":         0,
            "Temporario":        0,
            "Removido":          0,
            "ImportadoRepetido": 0,
            "DataIns":           datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        instance.fields.update(kwargs)
        return instance

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


class DischargeFlow:
    def __init__(self, json: dict):
        self.fields = {
            "CoefA":                 json.get("Coef_a"),
            "CoefH0":                json.get("Coef_h0"),
            "CoefN":                 json.get("Coef_n"),
            "CoefA0":                json.get("Coefa_0"),
            "CoefA1":                json.get("Coefa_1"),
            "CoefA2":                json.get("Coefa_2"),
            "CoefA3":                json.get("Coefa_3"),
            "CotaMaxima":            json.get("Cota_Maxima"),
            "CotaMinima":            json.get("Cota_Minima"),
            "DataAlt":               json.get("Data_Ultima_Alteracao"),
            "NivelConsistencia":     json.get("Nivel_Consistencia"),
            "NumeroCurva":           json.get("Numero_Curva"),
            "PeriodovalidadeFim":    json.get("Periodo_Validade_Fim"),
            "PeriodovalidadeInicio": json.get("Periodo_Validade_Inicio"),
            "TabelaPassoCota":       json.get("Tabela_Passo_Cota"),
            "TipoCurva":             json.get("Tipo_Curva"),
            "TipoEquacao":           json.get("Tipo_Equacao"),
            "EstacaoCodigo":         json.get("codigoestacao")
        }


class WaterQuality:
    def __init__(self, json: dict):
        self.fields = {
            "n245T":                       json.get("100_2_4_5_t_mgl"),
            "n245TP":                      json.get("101_2_4_5_tp_mgl"),
            "n246Triclorofenol":           json.get("102_2_4_6_Triclorofenol_mgl"),
            "Acido24Diclorofenoxiacetico": json.get("103_Acido_2_4_Diclorofenoxiacetico_mgl"),
            "Aldrin":                      json.get("104_Aldrin_mgl"),
            "AzinfosEtil":                 json.get("105_Azinfosetil_mgl"),
            "Benzeno":                     json.get("106_Benzeno_mgl"),
            "BenzoAPireno":                json.get("107_Benzoapireno_mgl"),
            "BHC":                         json.get("108_BHC_mgl"),
            "BifenilasPolicloradas":       json.get("109_Bifenilaspolicloradas_mgl"),
            "Escherichia":                 json.get("10_Escherichiacoli_ufc_100ml"),
            "Carbaril":                    json.get("110_Carbaril_mgl"),
            "Clordano":                    json.get("111_Clordano_mgl"),
            "DDEPP":                       json.get("112_DDEPP_mgl"),
            "DDT":                         json.get("113_DDT_mgl"),
            "Demeton":                     json.get("114_Demeton_mgl"),
            "Diazinon":                    json.get("115_Diazinon_mgl"),
            "Dieldrin":                    json.get("116_Dieldrin_mgl"),
            "DodecacloroNonacloro":        json.get("117_Dodecaclorononacloro_mgl"),
            "DySystonDisulfton":           json.get("118_Dysystondisulfton_mgl"),
            "Endossulfan":                 json.get("119_Endossulfan_mgl"),
            "FitoplanctonQuantitativo":    json.get("11_Fitoplancton_Quantitativo_celulas_100ml"),
            "Endrin":                      json.get("120_Endrin_mgl"),
            "EpoxidoHeptacloro":           json.get("121_Epoxidoheptacloro_mgl"),
            "Ethion":                      json.get("122_Ethion_mgl"),
            "Gution":                      json.get("123_Gution_mgl"),
            "Heptacloro":                  json.get("124_Heptacloro_mgl"),
            "Lindano":                     json.get("125_Lindano_mgl"),
            "Malation":                    json.get("126_Malation_mgl"),
            "MetilParation":               json.get("127_Metilparation_mgl"),
            "Metoxicloro":                 json.get("128_Metoxicloro_mgl"),
            "Paration":                    json.get("129_Paration_mgl"),
            "FosforoTotal":                json.get("12_Fosforo_Total_mgl)"),
            "Pentaclorofenol":             json.get("130_Pentaclorofenol_mgl"),
            "Phosdrin":                    json.get("131_Phosdrin_mgl"),
            "TetracloretoCarbono":         json.get("132_Tetra_Cloreto_Carbono_mgl"),
            "Tetracloroeteno":             json.get("133_Tetra_Cloro_Eteno_mgl"),
            "Toxafeno":                    json.get("134_Toxafeno_mgl"),
            "Tricloroeteno":               json.get("135_Tricloro_Eteno_mgl"),
            "Algas":                       json.get("136_Algas_n_upa_ml"),
            "Amoniaco":                    json.get("137_Amoniaco_mgl"),
            "BacteriasHeterotroficas":     json.get("138_Bacterias_Heterotroficas_ufc_ml"),
            "CloroResidual":               json.get("139_Cloro_Residual_mgl"),
            "Nitratos":                    json.get("13_Nitratos_mgl_n)"),
            "Colifagos":                   json.get("140_Colifagos_nmp_100ml"),
            "ContagemBacteriasPlaca":      json.get("141_Contagem_Bacterias_Placa_ufc_ml"),
            "EnteroBacteriasPatogenicas":  json.get("142_Entero_Bacterias_Patogenicas_n_org_ml"),
            "Fungos":                      json.get("143_Fungos_ufc_ml"),
            "NitrogenioAlbuminoide":       json.get("144_Nitrogenio_Albuminoide_mgl"),
            "Protozoarios":                json.get("145_Protozoarios_n_org_ml"),
            "Salmonelas":                  json.get("146_Salmonelas_nmp_ml"),
            "ZooplanctonTotal":            json.get("147_Zooplanctontotal_n_org_ml"),
            "NitrogenioAmoniacal":         json.get("14_Nitrogenio_Amoniacal_mgl"),
            "NitrogenioTotal":             json.get("15_Nitrogenio_Total_mgl_n"),
            "OrtofosfatoTotal":            json.get("16_Ortofosfato_Total_mgl_po4"),
            "OD":                          json.get("17_OD_mgl_02"),
            "pH":                          json.get("18_PH"),
            "SolDissolvidosTotais":        json.get("19_Soldissolvidos_Totais_mgl"),
            "AlcalinidadeTotal":           json.get("1_Alcalinidade_Total_mgl_caco3"),
            "SolSuspensaoTotais":          json.get("20_Solsuspensao_Totais_mgl"),
            "TempAmostra":                 json.get("21_Temperatura_Amostra_c"),
            "TempAr":                      json.get("22_Tempar_c"),
            "Transparencia":               json.get("23_Transparencia_m"),
            "Turbidez":                    json.get("24_Turbidez_ntu"),
            "Acidez":                      json.get("25_Acidez_mgl_caco3"),
            "AlcalinidadeCO3":             json.get("26_Alcalinidade_CO3_mgl"),
            "AlcalinidadeHCO3":            json.get("27_Alcalinidade_HCO3_mgl"),
            "AlcalinidadeOH":              json.get("28_Alcalinidade_OH_mgl"),
            "Aluminiodissolvido":          json.get("29_Aluminio_Dissolvido_mgl"),
            "CarbonoOrganicoTotal":        json.get("2_Carbono_Organico_Total_mgl"),
            "Aluminio":                    json.get("30_Aluminio_mgl_al"),
            "AmoniaNaoIonizavel":          json.get("31_Amonia_Nao_Ionizavel_mgl_nh3"),
            "Arsenio":                     json.get("32_Arsenio_mgl"),
            "Bario":                       json.get("33_Bario_mgl_ba"),
            "Berilio":                     json.get("34_Berilio_mgl"),
            "BismutoTotal":                json.get("35_Bismuto_Total_mgl"),
            "Borodissolvido":              json.get("36_Borodissolvido_mgl"),
            "Boro":                        json.get("37_Boro_mgl_b"),
            "Cadmio":                      json.get("38_Cadmio_mgl_cd"),
            "CalcioTotal":                 json.get("39_Calcio_Total_mgl"),
            "Cloretos":                    json.get("3_Cloretos_mgl_cl"),
            "Chumbo":                      json.get("40_Chumbo_mgl"),
            "Cianetolivre":                json.get("41_Cianeto_Livre_mgl"),
            "Cianetos":                    json.get("42_Cianetos_mgl_cn"),
            "Cobalto":                     json.get("43_Cobalto_mgl_co"),
            "Cobredissolvido":             json.get("44_Cobre_Dissolvido_mgl"),
            "Cobre":                       json.get("45_Cobre_mgl_cu"),
            "ColiformesFecais":            json.get("46_Coliformes_Fecais_nmp_100ml"),
            "ColiformesTotais":            json.get("47_Coliformes_Totais_nmp_100ml"),
            "CompostosOrganoclorados":     json.get("48_Compostos_Organo_Clorados_mgl"),
            "CompostosOrganofosforados":   json.get("49_Compostos_Organo_Fosforados_mgl"),
            "CondutividadeEletrica":       json.get("50_Condutivida_de_Eletrica_us_cm_a_20c"),
            "Cor":                         json.get("51_COR_mg_pt_col"),
            "CromoHexavalente":            json.get("52_Cromo_Hexavalente_mgl"),
            "CromoTotal":                  json.get("53_Cromo_Total_mgl_cr"),
            "CromoTrivalente":             json.get("54_Cromo_Trivalente_mgl"),
            "Densidadecianobacterias":     json.get("55_Densidade_Ciano_Bacterias_cel_ml"),
            "Detergentes":                 json.get("56_Detergentes_mgl_las"),
            "Dureza":                      json.get("57_Dureza_mgl_caco3"),
            "Durezamagnesio":              json.get("58_Dureza_Magnesio_mgl_mgco3"),
            "DurezaTotal":                 json.get("59_Dureza_Total_mgl"),
            "ColiformesTermotolerantes":   json.get("5_Coliformes_Termo_Tolerantes_ufc_100ml"),
            "EstreptococosFecais":         json.get("61_Estreptococos_Fecais_nmp_100ml"),
            "FerroDissolvido":             json.get("62_Ferro_Dissolvido_mgl"),
            "FerroTotal":                  json.get("63_Ferro_Total_mgl"),
            "Fluoretos":                   json.get("64_Fluoretos_mgl"),
            "FosfatoTotal":                json.get("65_Fosfato_Total_mgl"),
            "Hidrocarbonetos":             json.get("66_Hidrocarbonetos_mgl"),
            "IndiceFenois":                json.get("67_Indicefenois_mgl_c6h5oh"),
            "IQA":                         json.get("68_IQA"),
            "Litio":                       json.get("69_Litio_mgl"),
            "CondutividadeEspecifica":     json.get("6_Condutividade_Especifica_25oc_us_cm_a_25c"),
            "MagnesioTotal":               json.get("70_Magnesio_Total_mgl"),
            "Manganes":                    json.get("71_Manganes_mgl"),
            "Mercurio":                    json.get("72_Mercurio_mgl"),
            "Niquel":                      json.get("73_Niquel_mgl"),
            "Nitritos":                    json.get("74_Nitritos_mgl"),
            "NitrogenioOrganico":          json.get("75_Nitrogenio_Organico_mgl"),
            "NitrogenioTotalKJELDAHL":     json.get("76_Nitrogenio_Total_kjeldahl_mgl"),
            "OleosGraxas":                 json.get("77_Oleos_graxas_mgl"),
            "ODsaturacao":                 json.get("78_OD_perc_saturacao"),
            "PotassioTotal":               json.get("79_Potassio_Total_mgl"),
            "DBO":                         json.get("7_DBO_mgl_02)"),
            "Prata":                       json.get("80_Prata_mgl"),
            "ParametroProfundidade":       json.get("81_Parametro_Profundidade_m"),
            "Selenio":                     json.get("82_Selenio_mgl"),
            "SilicaDissolvida":            json.get("83_Silicadissolvida_mgl"),
            "SodioTotal":                  json.get("84_Sodiototal_mgl"),
            "SolDissolvidosFixos":         json.get("85_Soldissolvidos_Fixos_mgl_a_180c)"),
            "SolDissolvidosVolateis":      json.get("86_Soldissolvidos_Volateis_mgl"),
            "SolSuspensaoFixos":           json.get("87_Sol_Suspensao_Fixos_mgl"),
            "SolSuspensaoVolateis":        json.get("88_Sol_Suspensao_Volateis_mgl"),
            "SolFixos":                    json.get("89_Solfixos_mgl"),
            "DescargaLiquida":             json.get("8_Descarga_Liquida_m3s"),
            "SolSedimentaveis":            json.get("90_Sol_sedimentaveis_mgl"),
            "SolTotais":                   json.get("91_Sol_totais_mgl"),
            "SolVolateis":                 json.get("92_Sol_Volateis_mgl"),
            "Sulfatos":                    json.get("93_Sulfatos_mgl"),
            "Sulfetos":                    json.get("94_Sulfetos_mgl"),
            "UranioTotal":                 json.get("95_Uranio_Total_mgl"),
            "Vanadio":                     json.get("96_Vanadio_mgl"),
            "Zinco":                       json.get("97_Zinco_mgl"),
            "n11Dicloroeteno":             json.get("98_1_1_Dicloroeteno_mgl"),
            "n12Dicloroetano":             json.get("99_1_2_Dicloroetano_mgl"),
            "DQO":                         json.get("9_DQO_mgl_02)"),
            "Choveu":                      json.get("Choveu"),
            "Data":                        json.get("Data_Hora_Dado"),
            "DataAlt":                     json.get("Data_Ultima_Alteracao"),
            "NivelConsistencia":           json.get("Nilvel_ConsistÃªncia"),
            "NumMedicao":                  json.get("Num_Medicao"),
            "PosHorizColeta":              json.get("Posicao_Horizontal_Coleta"),
            "PosVertColeta":               json.get("Posicao_Vertical_Coleta"),
            "Profundidade":                json.get("Profundidade_m"),
            "EstacaoCodigo":               json.get("codigoestacao")
        }


class WaterQualityStatus:
    def __init__(self, json: dict):
        for i in range(1, 148):
            self.fields = {}
            self.fields[f"QualAgua{i:03d}Status"] = json.get(f"{i}_Status")


class Granulometry:
    def __init__(self, json: dict):
        self.fields = {
            "EstacaoCodigo":             json.get("codigoestacao"),
            "NivelConsistencia":         json.get("Nivel_Consistencia"),
            "Data":                      json.get("Data_Dado"),
            # "HoraInicial":               json.get("Hora_Final"),
            # "HoraFinal":                 json.get("Hora_Inicial"),
            "Cota":                      json.get("Cota_cm"),
            "Largura":                   json.get("Largura_m"),
            "TipoAmostra":               json.get("Tipo_Amostra"),
            "TipoColeta":                json.get("Tipo_Coleta"),
            "TipoEquip":                 json.get("Tipo_Equip"),
            "ProfTotal":                 json.get("Prof_Total_m"),
            "OrdemColeta":               json.get("Ordem_Coleta"),
            "DistPTOInicial":            json.get("Dist_Pto_Inicial_m"),
            "ChuvaUlt48":                json.get("Chuva_Ult_48h"),
            "MatFundo15_9":              json.get("MatFundo_15_9_mm"),
            "MatFundo8_0":               json.get("MatFundo_8_0_mm"),
            "MatFundo4_0":               json.get("MatFundo_4_0_mm"),
            "MatFundo2_0":               json.get("MatFundo_2_0_mm"),
            "MatFundo1_0":               json.get("MatFundo_1_0_mm"),
            "MatFundo0_5":               json.get("MatFundo_0_5_mm"),
            "MatFundo0_25":              json.get("MatFundo_0_25_mm"),
            "MatFundo0_125":             json.get("MatFundo_0_125_mm"),
            "MatFundo0_0625":            json.get("MatFundo_0_625_mm"),
            "MatFundoArgila":            json.get("MatFundo_Argila_%"),
            "MatFundoSilte":             json.get("MatFundo_Silte_%"),
            "MatFundoAreia":             json.get("MatFundo_Areia_%"),
            "MatFundoPedregulho":        json.get("MatFundo_Pedregulho_%"),
            "MatFundo0_0_a_0_0156":      json.get("MatFundo_0_0_a_0_0156_mm"),
            "MatFundo0_0157_a_0_02":     json.get("MatFundo_0_0157_a_0_02_mm"),
            "MatFundo0_0201_a_0_0625":   json.get("MatFundo_0_0201_a_0_0625_mm"),
            "MatFundo0_0626_a_0_1250":   json.get("MatFundo_0_0626_a_0_1250_mm"),
            "MatFundo0_1251_a_0_25":     json.get("MatFundo_0_1251_a_0_25_mm"),
            "MatFundo0_2501_a_0_5":      json.get("MatFundo_0_2501_a_0_5_mm"),
            "MatFundo0_501_a_1_0":       json.get("MatFundo_0_501_a_1_0_mm"),
            "MatFundo1_0001_a_2_0":      json.get("MatFundo_1_0001_a_2_0_mm"),
            "MatFundo2_0001_a_4_0":      json.get("MatFundo_2_0001_a_4_0_mm"),
            "MatFundo4_0001_a_8_0":      json.get("MatFundo_4_0001_a_8_0_mm"),
            "MatFundo8_0001_a_16_000":   json.get("MatFundo_8_0001_a_16_000_mm"),
            "MatFundoD10":               json.get("MatFundo_D10_mm"),
            "MatFundoD16":               json.get("MatFundo_D16_mm"),
            "MatFundoD35":               json.get("MatFundo_D35_mm"),
            "MatFundoD50":               json.get("MatFundo_D50_mm"),
            "MatFundoD65":               json.get("MatFundo_D65_mm"),
            "MatFundoD84":               json.get("MatFundo_D84_mm"),
            "MatFundoD90":               json.get("MatFundo_D90_mm"),
            "MatArrasteVazao":           json.get("MatArraste_Vazao_m3_s"),
            "MatArrasteLargRio":         json.get("MatArraste_LargRio_m"),
            "MatArrasteLargEquip":       json.get("MatArraste_LargEquip_m"),
            "MatArrastePesoMat":         json.get("MatArraste_PesoMat_g"),
            "MatArrasteVelMedia":        json.get("MatArraste_VelMedia_m_s"),
            "MatArrasteTempAgua":        json.get("MatArraste_TempAgua_C"),
            "MatArrasteTempAr":          json.get("MatArraste_TempAr_C"),
            "MatArrasteTempoColeta":     json.get("MatArraste_TempoColeta_min"),
            "MatArrasteArraste":         json.get("MatArraste_Arraste_t_dia"),
            "MatArraste15_9":            json.get("MatArraste_15_9_mm"),
            "MatArraste8_0":             json.get("MatArraste_8_0_mm"),
            "MatArraste4_0":             json.get("MatArraste_4_0_mm"),
            "MatArraste2_0":             json.get("MatArraste_2_0_mm"),
            "MatArraste1_0":             json.get("MatArraste_1_0_mm"),
            "MatArraste0_5":             json.get("MatArraste_0_5_mm"),
            "MatArraste0_25":            json.get("MatArraste_0_25_mm"),
            "MatArraste0_125":           json.get("MatArraste_0_125_mm"),
            "MatArraste0_0625":          json.get("MatArraste_0_0625_mm"),
            "MatArrasteArgila":          json.get("MatArraste_Argila_%"),
            "MatArrasteSilte":           json.get("MatArraste_Silte_%"),
            "MatArrasteAreia":           json.get("MatArraste_Areia_%"),
            "MatArrastePedregulho":      json.get("MatArraste_Pedregulho_%"),
            "MatArraste0_0_a_0_0156":    json.get("MatArraste_0_0_a_0_0156_mm"),
            "MatArraste0_0157_a_0_02":   json.get("MatArraste_0_0157_a_0_02_mm"),
            "MatArraste0_0201_a_0_0625": json.get("MatArraste_0_0201_a_0_0625_mm"),
            "MatArraste0_0626_a_0_1250": json.get("MatArraste_0_0626_a_0_1250_mm"),
            "MatArraste0_1251_a_0_25":   json.get("MatArraste_0_1251_a_0_25_mm"),
            "MatArraste0_2501_a_0_5":    json.get("MatArraste_0_2501_a_0_5_mm"),
            "MatArraste0_501_a_1_0":     json.get("MatArraste_0_501_a_1_0_mm"),
            "MatArraste1_0001_a_2_0":    json.get("MatArraste_1_0001_a_2_0_mm"),
            "MatArraste2_0001_a_4_0":    json.get("MatArraste_2_0001_a_4_0_mm"),
            "MatArraste4_0001_a_8_0":    json.get("MatArraste_4_0001_a_8_0_mm"),
            "MatArraste8_0001_a_16_000": json.get("MatArraste_8_0001_a_16_000_mm"),
            "MatArrasteD10":             json.get("MatArraste_D10_mm"),
            "MatArrasteD16":             json.get("MatArraste_D16_mm"),
            "MatArrasteD35":             json.get("MatArraste_D35_mm"),
            "MatArrasteD50":             json.get("MatArraste_D50_mm"),
            "MatArrasteD65":             json.get("MatArraste_D65_mm"),
            "MatArrasteD84":             json.get("MatArraste_D84_mm"),
            "MatArrasteD90":             json.get("MatArraste_D90_mm"),
            "MatSusp15_9":               json.get("MatSusp_15_9_mm"),
            "MatSusp8_0":                json.get("MatSusp_8_0_mm"),
            "MatSusp4_0":                json.get("MatSusp_4_0_mm"),
            "MatSusp2_0":                json.get("MatSusp_2_0_mm"),
            "MatSusp1_0":                json.get("MatSusp_1_0_mm"),
            "MatSusp0_5":                json.get("MatSusp_0_5_mm"),
            "MatSusp0_25":               json.get("MatSusp_0_25_mm"),
            "MatSusp0_125":              json.get("MatSusp_0_125_mm"),
            "MatSusp0_0625":             json.get("MatSusp_0_0625_mm"),
            "MatSuspArgila":             json.get("MatSusp_Argila_%"),
            "MatSuspSilte":              json.get("MatSusp_Silte_%"),
            "MatSuspAreia":              json.get("MatSusp_Areia_%"),
            "MatSuspPedregulho":         json.get("MatSusp_Pedregulho_%"),
            "MatSusp0_0_a_0_0156":       json.get("MatSusp_0_0_a_0_0156_mm"),
            "MatSusp0_0157_a_0_02":      json.get("MatSusp_0_0157_a_0_02_mm"),
            "MatSusp0_0201_a_0_0625":    json.get("MatSusp_0_0201_a_0_0625_mm"),
            "MatSusp0_0626_a_0_1250":    json.get("MatSusp_0_0626_a_0_1250_mm"),
            "MatSusp0_1251_a_0_25":      json.get("MatSusp_0_1251_a_0_25_mm"),
            "MatSusp0_2501_a_0_5":       json.get("MatSusp_0_2501_a_0_5_mm"),
            "MatSusp0_501_a_1_0":        json.get("MatSusp_0_501_a_1_0_mm"),
            "MatSusp1_0001_a_2_0":       json.get("MatSusp_1_0001_a_2_0_mm"),
            "MatSusp2_0001_a_4_0":       json.get("MatSusp_2_0001_a_4_0_mm"),
            "MatSusp4_0001_a_8_0":       json.get("MatSusp_4_0001_a_8_0_mm"),
            "MatSusp8_0001_a_16_000":    json.get("MatSusp_8_0001_a_16_000_mm"),
            "MatSuspD10":                json.get("MatSusp_D10_mm"),
            "MatSuspD16":                json.get("MatSusp_D16_mm"),
            "MatSuspD35":                json.get("MatSusp_D35_mm"),
            "MatSuspD50":                json.get("MatSusp_D50_mm"),
            "MatSuspD65":                json.get("MatSusp_D65_mm"),
            "MatSuspD84":                json.get("MatSusp_D84_mm"),
            "MatSuspD90":                json.get("MatSusp_D90_mm"),
            "DataAlt":                   json.get("Data_Ultima_Alteracao")
        }

class CrossSection:
    def __init__(self, json: dict):
        self.fields = {
            "RegistroID":        json.get("Registro_ID"),
            "EstacaoCodigo":     json.get("codigoestacao"),
            "NivelConsistencia": json.get("Nivel_Consistencia"),
            "Data":              json.get("Data_Hora_Medicao"),
            "NumLevantamento":   json.get("Num_Levantamento"),
            "TipoSecao":         json.get("Tipo_Secao"),
            "NumVerticais":      json.get("Num_Verticais"),
            "DistanciaPIPF":     json.get("Distancia_pipf"),
            "EixoXDistMaxima":   json.get("Eixo_X_Dist_Maxima"),
            "EixoXDistMinima":   json.get("Eixo_X_Dist_Minima"),
            "EixoYCotaMaxima":   json.get("Eixo_Y_Cota_Maxima"),
            "EixoYCotaMinima":   json.get("Eixo_Y_Cota_Minima"),
            "ElmGeomPassoCota":  json.get("Elm_Geom_Passo_Cota"),
            "Observacoes":       json.get("Observacoes")
        }


class VerticalCrossSection:
    def __init__(self, json: dict, reg_id):
        self.fields = {
            "RegistroID": reg_id,
            "Cota":       json.get("Cota"),
            "Distancia":  json.get("Distancia")
        }
