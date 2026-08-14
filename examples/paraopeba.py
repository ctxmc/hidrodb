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

from sqlalchemy           import select, func

import hidrodb.database   as db
from hidrodb.models.hidro import Station, Stage

HIDRO_DB = db.DatabaseConnection("db/hidro.db", db.DatabaseType.HIDRO)

def get_minas_geojson():
    import geobr;
    mg = geobr.read_municipality(code_muni=31, year=2025)
    mg["code_muni"] = mg["code_muni"].astype(str)
    lon, lat = [], []
    for feature in mg.__geo_interface__["features"]:
        geom = feature["geometry"]
        coords = geom["coordinates"]
        if geom["type"] == "Polygon":
            for ring in coords:
                lon.extend([p[0] for p in ring] + [None])
                lat.extend([p[1] for p in ring] + [None])
        elif geom["type"] == "MultiPolygon":
            for poly in coords:
                for ring in poly:
                    lon.extend([p[0] for p in ring] + [None])
                    lat.extend([p[1] for p in ring] + [None])
    return lon, lat


def get_stations_data():
    statement= select(
        Station.Codigo, Station.Latitude, Station.Longitude
    ).distinct().where(Station.RioCodigo.in_([40300000, 58642000]))
    hidro_session = HIDRO_DB.get_session()
    return hidro_session.execute(statement).all()


def get_stage_data(stations_code):
    statement = select(
        Stage.EstacaoCodigo,
        Stage.Maxima,
        Stage.Minima,
        Stage.MediaAnual,
        func.strftime('%Y-%m-%d', Stage.Data).label('Data')
    ).where(Stage.EstacaoCodigo.in_(stations_code))
    hidro_session = HIDRO_DB.get_session()
    return hidro_session.execute(statement).all()


if __name__ == "__main__":
    mg_lon, mg_lat                            = get_minas_geojson()
    stations_code, stations_lat, stations_lon = zip(*get_stations_data())

    from plotly.subplots import make_subplots;
    import plotly.graph_objects as go;

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "map"}, {"type": "xy"}]],
        column_widths=[0.6, 0.4],
        subplot_titles=("Mapa", "Gráfico")
    )

    fig.add_trace(
        go.Scattermap(
            lon=mg_lon, lat=mg_lat,
            mode="lines",
            line=dict(color="black", width=1),
            hoverinfo="skip",
            name="Limite de Minas Gerais"
        ),
        row=1, col=1
    )


    fig.add_trace(
        go.Scattermap(
            lon=stations_lon, lat=stations_lat,
            mode="markers+text",
            hovertext=stations_code,
            hoverinfo="text",
            marker=dict(size=8, color="red"),
            name="Estações"
        ),
        row=1, col=1
    )

    stage_data = get_stage_data(stations_code)
    codes  = [s.EstacaoCodigo for s in stage_data]
    dates  = [s.Data for s in stage_data]

    media  = [s.MediaAnual for s in stage_data]
    fig.add_trace(
        go.Bar(x=dates, y=media,
               hovertext=codes,
               hoverinfo="text",
               name="Média Anual"),
        row=1, col=2
    )

    maxima = [s.Maxima for s in stage_data]
    fig.add_trace(
        go.Bar(x=dates, y=maxima,
               hovertext=codes,
               hoverinfo="text",
               name="Máxima"),
        row=1, col=2
    )

    minima = [s.Minima for s in stage_data]
    fig.add_trace(
        go.Bar(x=dates, y=minima,
               hovertext=codes,
               hoverinfo="text",
               name="Minima"),
        row=1, col=2
    )

    valid_lon = [x for x in mg_lon if x is not None]
    valid_lat = [y for y in mg_lat if y is not None]
    fig.update_layout(
        map=dict(
            bounds=dict(
                west=min(valid_lon),
                east=max(valid_lon),
                south=min(valid_lat),
                north=max(valid_lat)
            )
        )
    )

    fig.write_html("examples/paraopeba.html")
