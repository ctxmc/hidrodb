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

import pytest
from unittest.mock import patch, MagicMock

from datetime import datetime, timedelta

import hidrodb.jobs

@patch('hidrodb.jobs.count_client')
@patch('hidrodb.jobs.add_token')
@patch('hidrodb.jobs.update_token')
@patch('hidrodb.jobs.get_credentials')
@patch('hidrodb.jobs.request_token')
@patch('hidrodb.jobs.get_token_model')
def test_get_token_add_new_token(mock_model,  mock_request, mock_creds,
                                 mock_update, mock_add,     mock_count):
    mock_model.return_value   = None
    mock_creds.return_value   = MagicMock(ID="test_id", Password="test_pass")
    mock_request.return_value = ("new_token", datetime.now() + timedelta(hours=1))
    mock_count.return_value   = 0

    result = hidrodb.jobs.get_token()

    mock_model.assert_called_once()
    mock_creds.assert_called_once()
    mock_request.assert_called_once_with("test_id", "test_pass")
    mock_count.assert_called_once()
    mock_update.assert_not_called()
    mock_add.assert_called_once()

    assert result == "new_token"

@patch('hidrodb.jobs.trigger_job')
@patch('hidrodb.jobs.insert_jobs')
@patch('hidrodb.jobs.count_job')
@pytest.mark.parametrize("job_config", [
    hidrodb.jobs.JobConfig.Base.BASIN,
    hidrodb.jobs.JobConfig.Base.SUB_BASIN,
    hidrodb.jobs.JobConfig.Base.ENTITY,
    hidrodb.jobs.JobConfig.Base.TOWNSHIP,
    hidrodb.jobs.JobConfig.Base.RIVER,
    hidrodb.jobs.JobConfig.Base.STATE,
])
def test_check_base_job(mock_count_jobs, mock_insert_jobs, mock_trigger_job, job_config):

    mock_count_jobs.side_effect = [0, 1, 1]
    hidrodb.jobs.check_base_job(job_config)
    mock_insert_jobs.assert_called_once()
    mock_trigger_job.assert_called_once()


CORRUPTED_DATES_PARAMS = [
    (3154001, "2911-12-01 00:00:00", "2026-07-01 00:00:00", 4),
    (1048002, "1996-12-01 00:00:00", "1977-11-01 00:00:00", 4),
    (1740000, "2009-01-02 00:00:00", "2009-01-01 00:00:00", 4),
    (849001,  "1996-12-01 00:00:00", "1985-03-01 00:00:00", 4),
    (650000,  "1996-12-01 00:00:00", "1982-01-01 00:00:00", 4),
    (1748006, "1980-09-01 00:00:00", "1980-01-01 00:00:00", 4),
    (1036042, "1982-09-01 00:00:00", "1973-01-01 00:00:00", 4),
    (338025,  "1977-03-01 00:00:00", "1931-02-01 00:00:00", 4),
    (2652043, "1989-07-01 00:00:00", "1987-08-01 00:00:00", 4),
    (2950036, "1966-01-02 00:00:00", "1966-01-01 00:00:00", 4),
    (2056005, "2018-01-02 00:00:00", "2018-01-01 00:00:00", 4),
]

@pytest.mark.parametrize("station_code, start_date, end_date, expected_status", CORRUPTED_DATES_PARAMS)
def test_process_period_returns_corrupted_for_invalid_dates(station_code, start_date, end_date, expected_status):
    """Test that process_period returns CORRUPTED status when FromDate > ToDate."""

    from hidrodb.jobs import JobConfig, process_period
    result = process_period(station_code, start_date, end_date, JobConfig.Series.RAIN)

    assert len(result) == 1, f"Expected 1 job, got {len(result)}"
    assert result[0].Status == expected_status, \
        f"Expected status {expected_status}, got {result[0].Status}"
    assert result[0].StationID == station_code
    assert result[0].FromDate  == datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    assert result[0].ToDate    == datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")


def test_process_period_returns_corrupted_for_future_date():
    """Test that future start date returns CORRUPTED."""

    from hidrodb.jobs import JobConfig, process_period
    future_date = (datetime.today() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
    result = hidrodb.jobs.process_period(123456, future_date, "2020-01-01 00:00:00", JobConfig.Series.RAIN)

    assert len(result) == 1
    assert result[0].Status == 4
