import pytest

from havenlighting import HavenClient
from havenlighting.config import DEVICE_ID
from havenlighting.credentials import Credentials
from havenlighting.exceptions import AuthenticationError, DeviceError


def test_client_initialization():
    client = HavenClient()
    assert isinstance(client._credentials, Credentials)
    assert not client._credentials.is_authenticated
    assert client._locations == {}
    assert client._lights == {}

def test_authentication_success(client, mocker):
    # Create credentials first
    credentials = Credentials()
    
    # Mock the internal request method
    mock_request = mocker.patch.object(credentials, '_make_request_internal')
    mock_request.return_value = {
        "success": True,
        "data": {
            "token": "test_token",
            "refreshToken": "test_refresh_token",
            "id": 123
        }
    }
    
    client._credentials = credentials
    assert client.authenticate("test@example.com", "password")
    assert client._credentials.is_authenticated
    mock_request.assert_called_once_with(
        "POST",
        "/User/authenticate",
        json={
            "email": "test@example.com",
            "password": "password",
            "deviceId": DEVICE_ID
        },
        auth_required=False
    )

def test_authentication_failure(client, mocker):
    # Create credentials first
    credentials = Credentials()
    
    # Mock failed authentication
    mock_request = mocker.patch.object(credentials, '_make_request_internal')
    mock_request.return_value = {
        "success": False,
        "returnCode": 600,
        "severityLevel": 1,
        "message": "Password is incorrect",
        "data": None
    }

    client._credentials = credentials
    
    assert not client.authenticate("test@example.com", "wrong_password")
    assert not client._credentials.is_authenticated

def test_discover_locations(authenticated_client, mock_location_response, mocker):
    # Mock the location discovery request
    mock_request = mocker.patch.object(authenticated_client._credentials, 'make_request')
    mock_request.return_value = mock_location_response
    
    locations = authenticated_client.discover_locations()
    assert len(locations) == 1
    location = next(iter(locations.values()))
    assert location.name == "Test Location"

def test_discover_locations_unauthenticated(client):
    with pytest.raises(AuthenticationError):
        client.discover_locations() 