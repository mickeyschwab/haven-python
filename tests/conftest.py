import pytest
from havenlighting import HavenClient
from havenlighting.credentials import Credentials

@pytest.fixture
def client():
    return HavenClient()

@pytest.fixture
def authenticated_client(client, mocker):
    # Create credentials first
    credentials = Credentials()

    # Mock successful authentication
    mock_auth = mocker.patch.object(credentials, '_make_request_internal')
    mock_auth.return_value = {
        "id": 123,
        "username": "test@example.com",
        "token": "test_token",
        "refreshToken": "test_refresh_token",
        "userType": 1
    }

    client._credentials = credentials
    client.authenticate("test@example.com", "test_password")
    return client

@pytest.fixture
def mock_location_response():
    return {
        "userId": 123,
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "Location",
        "defaultLocationId": 123,
    }

@pytest.fixture
def mock_lights_response():
    return {
        "locationId": 123,
        "name": "Test Location",
        "lights": [
            {
                "lightId": 456,
                "name": "Test Light",
                "lightingStatusId": 1,
                "lightBrightnessId": 10,
                "colorId": 11,
                "patternSpeedId": 0,
            }
        ],
    }
