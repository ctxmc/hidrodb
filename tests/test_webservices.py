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


@patch('hidrodb.webservices.requests.get')
def test_request_hidro_ws_json_exception(mock_get):
    """Test handling of JSON decode error on successful response."""

    mock_response                  = Mock()
    mock_response.ok               = True
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value          = mock_response

    result = request_hidro_ws("/endpoint", {})

    assert result is None


@patch('hidrodb.webservices.request_hidro_ws')
def test_request_token_success(mock_request):
    """Test successful token retrieval."""

    mock_request.return_value = {
        "items": {
            "tokenautenticacao": "abc123token",
            "validade": "Mon Jan 15 14:30:00 GMT-03:00 2024"
        }
    }

    result = request_token("client123", "pass456")

    assert result[0] == "abc123token"
    assert isinstance(result[1], datetime)
    assert result[1] == datetime(2024, 1, 15, 14, 30, 0)

    mock_request.assert_called_once_with(
        "/EstacoesTelemetricas/OAUth/v1",
        {
            "accept": "*/*",
            "Identificador": "client123",
            "Senha": "pass456"
        },
        {}
    )


@patch('hidrodb.webservices.request_hidro_ws')
@patch('hidrodb.webservices.time.sleep')
def test_request_token_retry_then_success(mock_sleep, mock_request):
    """Test retry logic when first attempt fails."""
    mock_request.side_effect = [
        Exception("Connection error"),
        {
            "items": {
                "tokenautenticacao": "token_after_retry",
                "validade": "Tue Feb 20 10:00:00 GMT-03:00 2024"
            }
        }
    ]

    result = request_token("client123", "pass456", max_retries=3, retry_delay=2)

    assert result[0]               == "token_after_retry"
    assert mock_request.call_count == 2
    mock_sleep.assert_called_once_with(2)
