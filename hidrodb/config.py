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

"""
Provides general config to HidroDB application.
"""

import logging

HIDRO_PATH  = None
CLIENT_PATH = None
MAX_WOKERS  = None
BATCH_SIZE  = None

def setup_logger(log_level):
    """ Setup logger object accross application. """

    TRACE = 15
    setattr(logging.Logger, 'trace', _make_logger(TRACE))
    logging.addLevelName(TRACE, 'TRACE')
    VERBOSE = 5
    setattr(logging.Logger, 'verbose', _make_logger(VERBOSE))
    logging.addLevelName(VERBOSE, 'VERBOSE')
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s]: %(message)s'
    )


def _make_logger(level):
    """ Helper method to create TRACE and VERBOSE logger modes. """

    def logger(self, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)
    return logger


def setup_database(user_id, password):
    """ Setup Hidro and Client Database. """

    from database import DatabaseType, init_db, count_client, insert_credentials;

    init_db(CLIENT_PATH, DatabaseType.CLIENT)
    init_db(HIDRO_PATH, DatabaseType.HIDRO)
    if not count_client(Credentials):
        if not user_id:
            user_id = input("Enter API username: ")
        if not password:
            import getpass;
            password = getpass.getpass("Enter API password: ")
        insert_credentials(user_id, password)


from enum import StrEnum
from webservices   import *
from models.hidro  import *
from models.client import *

class HidroResource(StrEnum):
    """ Enum to hold basic resources data that does not require Threads. """

    BASIN             = "Bacia"
    SUB_BASIN         = "SubBacia"
    ENTITY            = "Entidade"
    TOWNSHIP          = "Municipio"
    RIVER             = "Rio"
    STATE             = "Estado"

    def get_model(self):
        mapping = {
            HidroResource.BASIN:     Basin,
            HidroResource.SUB_BASIN: SubBasin,
            HidroResource.ENTITY:    Entity,
            HidroResource.TOWNSHIP:  Township,
            HidroResource.RIVER:     River,
            HidroResource.STATE:     State,
        }
        return mapping[self]

    def get_endpoint(self):
        mapping = {
            HidroResource.BASIN:     HidroEndpoint.BASIN,
            HidroResource.SUB_BASIN: HidroEndpoint.SUB_BASIN,
            HidroResource.ENTITY:    HidroEndpoint.ENTITY,
            HidroResource.TOWNSHIP:  HidroEndpoint.TOWNSHIP,
            HidroResource.RIVER:     HidroEndpoint.RIVER,
            HidroResource.STATE:     HidroEndpoint.STATE,
        }
        return mapping[self]

class JobConfig(StrEnum):
    """ Enum to hold Hidro Jobs that will run with threads. """
    STATION           = "Estacao"
    RAIN              = "Chuvas"
    DISCHARGE_SUMMARY = "ResumoDescarga"
    DISCHARGE_FLOW    = "CurvaDescarga"
    SEDIMENTS         = "Sedimentos"
    WATER_QUALITY     = "QualAgua"
    STAGE             = "Cotas"
    GRANULOMETRY      = "Granulometria"
    CROSS_SECTION     = "PerfilTransversal"
    FLOW_RATE         = "Vazoes"

    def get_job_model(self):
        if self == JobConfig.STATION:
            return StationJobs
        else:
            return SeriesJobs

    def get_hidro_model(self):
        mapping = {
            JobConfig.STATION:           Station,
            JobConfig.RAIN:              Rain,
            JobConfig.DISCHARGE_SUMMARY: DischargeSummary,
            JobConfig.DISCHARGE_FLOW:    DischargeFlow,
            JobConfig.SEDIMENTS:         Sediments,
            JobConfig.WATER_QUALITY:     WaterQuality,
            JobConfig.STAGE:             Stage,
            JobConfig.GRANULOMETRY:      Granulometry,
            JobConfig.CROSS_SECTION:     CrossSection,
            JobConfig.FLOW_RATE:         FlowRate,
        }
        return mapping[self]

    def get_endpoint(self):
        mapping = {
            JobConfig.STATION:           HidroEndpoint.STATION,
            JobConfig.RAIN:              HidroEndpoint.RAIN,
            JobConfig.DISCHARGE_SUMMARY: HidroEndpoint.DISCHARGE_SUMMARY,
            JobConfig.DISCHARGE_FLOW:    HidroEndpoint.DISCHARGE_FLOW,
            JobConfig.SEDIMENTS:         HidroEndpoint.SEDIMENTS,
            JobConfig.WATER_QUALITY:     HidroEndpoint.WATER_QUALITY,
            JobConfig.STAGE:             HidroEndpoint.STAGE,
            JobConfig.GRANULOMETRY:      HidroEndpoint.GRANULOMETRY,
            JobConfig.CROSS_SECTION:     HidroEndpoint.CROSS_SECTION,
            JobConfig.FLOW_RATE:         HidroEndpoint.FLOW_RATE,
        }
        return mapping[self]

