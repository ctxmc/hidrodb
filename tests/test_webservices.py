import pytest
from unittest.mock import patch, Mock

import requests
import json

from hidrodb.webservices import *

@patch('hidrodb.webservices.requests.get')
def test_request_hidro_ws_success(mock_get):
    """Test successful request returns JSON."""

    mock_response                   = Mock()
    mock_response.ok                = True
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value           = mock_response

    result = request_hidro_ws("/endpoint", {"Authorization": "Bearer token"})

    assert result == {"data": "test"}
    mock_get.assert_called_once_with(
        "https://www.ana.gov.br/hidrowebservice/endpoint",
        headers={"Authorization": "Bearer token"},
        params={}
    )

@patch('hidrodb.webservices.requests.get')
@patch('hidrodb.webservices.time.sleep')
def test_request_hidro_ws_error(mock_sleep, mock_get):
    """Test sleep on 503 code."""

    mock_response                   = Mock()
    mock_response.ok                = False
    mock_response.status_code       = 503
    mock_response.json.return_value = {"error": "Service Unavailable"}
    mock_get.return_value           = mock_response

    result = request_hidro_ws("/endpoint", {})

    assert result is None
    mock_sleep.assert_called_once_with(1)
