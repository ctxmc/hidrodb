import pytest

from hidrodb.config import *


def test_setup_logger_creates_custom_levels(caplog):
    import logging;

    VERBOSE = 5
    setup_logger(VERBOSE)
    caplog.set_level(VERBOSE)

    logging.getLogger().trace("trace message")
    assert "trace message" in caplog.text
    assert "TRACE" in caplog.text

    logging.getLogger().verbose("verbose message")
    assert "verbose message" in caplog.text
    assert "VERBOSE" in caplog.text


def test_setup_logger_respects_log_level(caplog):
    import logging;

    setup_logger(logging.WARNING)

    logging.getLogger().trace("should not appear")
    logging.getLogger().verbose("should not appear")
    logging.getLogger().warning("warning message")

    assert "should not appear" not in caplog.text
    assert "warning message" in caplog.text


def test_hidro_resource():
    from hidrodb.models.hidro  import Basin, SubBasin, Entity, Township, River, State;
    from hidrodb.webservices   import HidroEndpoint

    assert_data = [
        {'label': "Bacia",     'model': Basin,    'endpoint': HidroEndpoint.BASIN},
        {'label': "SubBacia",  'model': SubBasin, 'endpoint': HidroEndpoint.SUB_BASIN},
        {'label': "Entidade",  'model': Entity,   'endpoint': HidroEndpoint.ENTITY},
        {'label': "Municipio", 'model': Township, 'endpoint': HidroEndpoint.TOWNSHIP},
        {'label': "Rio",       'model': River,    'endpoint': HidroEndpoint.RIVER},
        {'label': "Estado",    'model': State,    'endpoint': HidroEndpoint.STATE}
    ]

    for index, resource in enumerate(HidroResource):
        assert assert_data[index]['label'] in resource
        assert assert_data[index]['model'] == resource.get_model()
        assert assert_data[index]['endpoint'] in resource.get_endpoint()


def test_hidro_job():
    from hidrodb.models.hidro  import Station, Rain, DischargeSummary, DischargeFlow, Sediments, WaterQuality, Stage, Granulometry, CrossSection, FlowRate;
    from hidrodb.webservices   import HidroEndpoint

    assert_data = [
        {'label': "Estacao",           'job_model': StationJobs, 'hidro_model': Station,          'endpoint': HidroEndpoint.STATION},
        {'label': "Chuvas",            'job_model': SeriesJobs,  'hidro_model': Rain,             'endpoint': HidroEndpoint.RAIN},
        {'label': "ResumoDescarga",    'job_model': SeriesJobs,  'hidro_model': DischargeSummary, 'endpoint': HidroEndpoint.DISCHARGE_SUMMARY},
        {'label': "CurvaDescarga",     'job_model': SeriesJobs,  'hidro_model': DischargeFlow,    'endpoint': HidroEndpoint.DISCHARGE_FLOW},
        {'label': "Sedimentos",        'job_model': SeriesJobs,  'hidro_model': Sediments,        'endpoint': HidroEndpoint.SEDIMENTS},
        {'label': "QualAgua",          'job_model': SeriesJobs,  'hidro_model': WaterQuality,     'endpoint': HidroEndpoint.WATER_QUALITY},
        {'label': "Cotas",             'job_model': SeriesJobs,  'hidro_model': Stage,            'endpoint': HidroEndpoint.STAGE},
        {'label': "Granulometria",     'job_model': SeriesJobs,  'hidro_model': Granulometry,     'endpoint': HidroEndpoint.GRANULOMETRY},
        {'label': "PerfilTransversal", 'job_model': SeriesJobs,  'hidro_model': CrossSection,     'endpoint': HidroEndpoint.CROSS_SECTION},
        {'label': "Vazoes",            'job_model': SeriesJobs,  'hidro_model': FlowRate,         'endpoint': HidroEndpoint.FLOW_RATE}
    ]

    for index, job_config in enumerate(JobConfig):
        assert assert_data[index]['label'] in job_config
        assert assert_data[index]['job_model']   == job_config.get_job_model()
        assert assert_data[index]['hidro_model'] == job_config.get_hidro_model()
        assert assert_data[index]['endpoint'] in job_config.get_endpoint()
