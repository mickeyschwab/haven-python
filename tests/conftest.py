import pytest
from havenlighting import HavenClient
from havenlighting.credentials import Credentials

@pytest.fixture
def client():
    return HavenClient()

@pytest.fixture
def authenticated_client(client, mocker):
    # Create credentials first
    client._credentials = Credentials()
    
    # Mock successful authentication
    mock_auth = mocker.patch.object(client._credentials, 'make_request')
    mock_auth.return_value = {
        "success": True,
        "data": {
            "token": "test_token",
            "refreshToken": "test_refresh_token",
            "id": "test_user_id"
        }
    }
    
    client.authenticate("test@example.com", "test_password")
    return client

@pytest.fixture
def mock_location_response():
    return {
        "success": True,
        "data": [
            {
                "locationId": "1",
                "ownerName": "Test Location",
                "name": "Test Location"
            }
        ]
    }

@pytest.fixture
def mock_lights_response():
    return {
        "success": True,
        "data": {
            "lights": [
                {
                    "lightId": "1",
                    "name": "Test Light",
                    "lightingStatusId": 1
                }
            ]
        }
    } 