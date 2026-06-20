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
from enum import StrEnum

from hidro_webservices   import *
from models.hidro_models import *

class HidroResource(StrEnum):
    BASIN             = "Bacia"
    SUB_BASIN         = "SubBacia"
    ENTITY            = "Entidade"
    TOWNSHIP          = "Municipio"
    RIVER             = "Rio"
    STATE             = "Estado"
    STATION           = "Estacao"

    def get_model(self):
        mapping = {
            HidroResource.BASIN:     Basin,
            HidroResource.SUB_BASIN: SubBasin,
            HidroResource.ENTITY:    Entity,
            HidroResource.TOWNSHIP:  Township,
            HidroResource.RIVER:     River,
            HidroResource.STATE:     State,
            HidroResource.STATION:   Station,
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
            HidroResource.STATION:   HidroEndpoint.STATION,
        }
        return mapping[self]
