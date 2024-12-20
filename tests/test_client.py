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

def test_token_refresh(client, mocker):
    credentials = Credentials()
    
    # Mock initial authentication
    mock_auth = mocker.patch.object(credentials, '_make_request_internal')
    mock_auth.return_value = {
        "success": True,
        "data": {
            "token": "initial_token",
            "refreshToken": "test_refresh_token",
            "id": 123
        }
    }
    
    client._credentials = credentials
    client.authenticate("test@example.com", "password")
    
    # Mock a 401 followed by successful refresh
    mock_request = mocker.patch.object(credentials, '_make_request_internal')
    mock_request.side_effect = [
        AuthenticationError("Token expired"),  # First call fails
        {  # Refresh token call succeeds
            "success": True,
            "data": {
                "token": "new_token",
                "refreshToken": "new_refresh_token",
                "id": 123
            }
        },
        {  # Original request succeeds with new token
            "success": True,
            "data": {"test": "data"}
        }
    ]
    
    # This should trigger the refresh flow
    result = client._credentials.make_request("GET", "/test/endpoint")
    
    assert result == {"success": True, "data": {"test": "data"}}
    assert mock_request.call_count == 3  # Original request + refresh + retry