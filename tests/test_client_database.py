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
from unittest.mock import patch

from hidrodb.database        import *
from hidrodb.database.client import *

@pytest.fixture
def client_db(tmp_path):
    """Create a temporary CLIENT database for testing."""

    db_path = str(tmp_path / "client.db")
    db_type = DatabaseType.CLIENT
    from hidrodb.database import _setup_db
    connection = _setup_db(db_path, db_type)
    with patch('hidrodb.database.client.CLIENT_DB', connection):
        yield connection
        ClientBase.metadata.drop_all(connection.engine)
        connection.close()


def test_insert_credentials_creates_entry(client_db):

    insert_credentials(user_id="test_user", password="test_pass")
    session = client_db.get_session()
    result = session.query(Credentials).filter_by(ID="test_user").first()
    assert result is not None
    assert result.ID == "test_user"
    assert result.Password == "test_pass"
    session.close()


def test_check_credetials(client_db):
    check_result = check_credentials()
    assert check_result == 0
    insert_credentials(user_id="test_user", password="test_pass")
    check_result = check_credentials()
    assert check_result == 1


def test_get_credentials(client_db):

    credentials = get_credentials()
    assert credentials == None

    insert_credentials(user_id="test_user", password="test_pass")
    credentials = get_credentials()
    assert credentials is not None
    assert credentials.ID == "test_user"
    assert credentials.Password == "test_pass"


def test_add_token(client_db):
    insert_credentials(user_id="test_user", password="test_pass")
    credential = get_credentials()
    from datetime import datetime, timedelta;
    expires = datetime.now() - timedelta(days=1)
    add_token(credential.RegistroID, "test_token", expires)
    session = client_db.get_session()
    result = session.query(Token).filter_by(CredentialID=credential.RegistroID).first()
    assert result is not None
    assert result.Token == "test_token"
    assert result.Expires is not None
    assert isinstance(result.Expires, datetime)
    session.close()


def test_get_token(client_db):
    insert_credentials(user_id="test_user", password="test_pass")
    credential = get_credentials()
    from datetime import datetime, timedelta;
    expires = datetime.now() - timedelta(days=1)
    add_token(credential.RegistroID, "test_token", expires)
    result = get_token_model()
    assert result is not None
    assert result.Token == "test_token"
    assert result.Expires is not None
    assert isinstance(result.Expires, datetime)


def test_update_token(client_db):
    insert_credentials(user_id="test_user", password="test_pass")
    credential = get_credentials()
    from datetime import datetime, timedelta
    expires = datetime.now() - timedelta(days=1)
    add_token(credential.RegistroID, "test_token", expires)
    token = get_token_model()
    update_token(token.RegistroID, "new_token", datetime.now())
    result = get_token_model()
    assert result is not None
    assert result.Token == "new_token"
    assert result.Expires is not None
    assert isinstance(result.Expires, datetime)
    assert result.Expires != token.Expires


@pytest.mark.parametrize("table_name, expected_result", [
    ("Bacia",     BaseJobs), ("SubBacia",  BaseJobs),
    ("Entidade",  BaseJobs), ("Municipio", BaseJobs),
    ("Rio",       BaseJobs), ("Estado",    BaseJobs)
])
def test_get_job_model(client_db, table_name, expected_result):
    model = get_job_model(table_name)
    assert model == expected_result


@pytest.fixture
def base_jobs():
    return [
        BaseJobs(HidroTable="Bacia",     Status=1),
        BaseJobs(HidroTable="SubBacia",  Status=1),
        BaseJobs(HidroTable="Entidade",  Status=1),
        BaseJobs(HidroTable="Municipio", Status=1),
        BaseJobs(HidroTable="Rio",       Status=1),
        BaseJobs(HidroTable="Estado",    Status=1),
    ]


@pytest.mark.parametrize("job_type, jobs", [
    (BaseJobs, "base_jobs"),
])
def test_insert_jobs(client_db, job_type, jobs, request):

    jobs = request.getfixturevalue(jobs)
    insert_jobs(jobs)
    session = client_db.get_session()
    inserted_jobs = session.query(job_type).all()
    assert len(inserted_jobs) == len(jobs)
    session.close()


@pytest.mark.parametrize("job", [pytest.param("base_jobs", marks=[])])
def test_update_base_jobs(client_db, job, request):

    jobs = request.getfixturevalue(job)
    session = client_db.get_session()
    session.add_all(jobs)
    session.commit()
    inserted_jobs = session.query(BaseJobs).all()
    assert len(inserted_jobs) == len(jobs)
    session.close()

    import random;
    from datetime import datetime;
    for job in jobs:
        job.Status = random.randint(2, 5)
        job.LastCheck = datetime.now()
    update_jobs(jobs, job.HidroTable)
    session = client_db.get_session()
    updated_jobs = session.query(BaseJobs).all()
    for updated_job in updated_jobs:
        assert 2 <= updated_job.Status <= 5
        assert updated_job.LastCheck is not None
        assert isinstance(job.LastCheck, datetime)
    session.close()


BASE_JOB_FILTERS = [
    ("Bacia",     None, False), ("SubBacia",  [],   False),
    ("Entidade",  [1],  False), ("Municipio", None, True),
    ("Rio",       [],   True),  ("Estado",    [1],  True),
]

@pytest.mark.parametrize("job_name, status, last_check", BASE_JOB_FILTERS)
def test_create_job_filters(client_db, job_name, status, last_check):
    model = get_job_model(job_name)
    result = create_job_filters(job_name, status, last_check)
    result_len = 1

    assert str(result[0]) == str(model.HidroTable == job_name)

    if status and not last_check:
        result_len += 1
        expected_status_filter = model.Status.in_(status)
        assert str(result[1]) == str(expected_status_filter)

    if last_check and not status:
        result_len += 1
        from datetime import datetime
        assert str(result[1]) == str(model.LastCheck < datetime.today())

    if last_check and status:
        result_len += 1
        from sqlalchemy import or_
        from datetime import datetime
        expected = or_(model.Status.in_(status), model.LastCheck < datetime.today())
        assert str(result[1]) == str(expected)

    assert len(result) == (result_len)


@pytest.mark.parametrize("job_type, jobs", [
    (BaseJobs, [
        BaseJobs(HidroTable="Bacia",     Status=1),
        BaseJobs(HidroTable="SubBacia",  Status=2),
        BaseJobs(HidroTable="Entidade",  Status=3),
        BaseJobs(HidroTable="Municipio", Status=4),
        BaseJobs(HidroTable="Rio",       Status=5),
    ]),
])
def test_count_jobs_by_status(client_db, job_type, jobs, request):
    hidro_tables = []
    for job in jobs:
        hidro_tables.append(job.HidroTable)
    insert_jobs(jobs)
    for index, table in enumerate(hidro_tables):
        result = count_job_by_status(table)
        if (index == 3):
            assert result == []
        else:
            assert result == [(index+1, 1)]


@pytest.mark.parametrize("job_type, jobs", [
    (BaseJobs, "base_jobs"),
])
def test_count_job(client_db, job_type, jobs, request):
    jobs = request.getfixturevalue(jobs)
    insert_jobs(jobs)
    for job_name, status, last_check in BASE_JOB_FILTERS:
        filters = create_job_filters(job_name, status, last_check)
        result = count_job(job_name, filters)
        if status and status[0] == 1:
            assert result == 1


@pytest.mark.parametrize("job_type, jobs", [
    (BaseJobs, "base_jobs"),
])
def test_get_jobs(client_db, job_type, jobs, request):
    jobs = request.getfixturevalue(jobs)
    insert_jobs(jobs)
    for job_name, status, last_check in BASE_JOB_FILTERS:
        filters = create_job_filters(job_name, status, last_check)
        result = get_jobs(job_name, filters)
        if status and status[0] == 1:
            assert len(result) == 1
