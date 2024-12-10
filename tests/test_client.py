import pytest
from havenlighting import HavenLightingClient, AuthResponse, AuthenticationError

def test_client_initialization():
    base_url = "https://test-api.example.com"
    client = HavenLightingClient(base_url)
    assert client.base_url == base_url
    assert not client.is_authenticated

def test_authentication_success(client, mocker):
    mock_response = mocker.patch("requests.request")
    mock_response.return_value.json.return_value = {
        "success": True,
        "data": {
            "token": "test_token",
            "refreshToken": "test_refresh_token",
            "id": "test_user_id"
        }
    }
    
    response = client.authenticate("test@example.com", "password")
    assert isinstance(response, AuthResponse)
    assert response.success
    assert response.token == "test_token"
    assert client.is_authenticated

def test_control_light(authenticated_client, mocker):
    mock_response = mocker.patch("requests.request")
    mock_response.return_value.json.return_value = {"success": True}
    
    response = authenticated_client.control_light(
        "test_location_id",
        [1, 2, 3],
        turn_on=True
    )
    assert response["success"] 