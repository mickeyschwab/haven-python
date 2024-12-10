import pytest
from havenlighting import HavenClient
from havenlighting.credentials import Credentials
from havenlighting.exceptions import AuthenticationError, DeviceError

def test_client_initialization():
    client = HavenClient()
    assert client._credentials is None
    assert client._locations == {}
    assert client._lights == {}

def test_authentication_success(client, mocker):
    # Create credentials first
    client._credentials = Credentials()
    
    # Mock the credentials make_request method
    mock_request = mocker.patch.object(client._credentials, 'make_request')
    mock_request.return_value = {
        "success": True,
        "data": {
            "token": "test_token",
            "refreshToken": "test_refresh_token",
            "id": "test_user_id"
        }
    }
    
    assert client.authenticate("test@example.com", "password")
    assert client._credentials.is_authenticated
    mock_request.assert_called_once_with(
        "POST",
        "/User/authenticate",
        json={
            "email": "test@example.com",
            "password": "password",
            "deviceId": "HavenLightingMobile"
        },
        auth_required=False,
        use_prod_api=False
    )

def test_authentication_failure(client, mocker):
    # Create credentials first
    client._credentials = Credentials()
    
    # Mock failed authentication
    mock_request = mocker.patch.object(client._credentials, 'make_request')
    mock_request.return_value = {
        "success": False,
        "message": "Invalid credentials"
    }
    
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