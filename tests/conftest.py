import pytest
from havenlighting import HavenLightingClient

@pytest.fixture
def client():
    return HavenLightingClient("https://havenwebservices-apiapp-test.azurewebsites.net/api/v2")

@pytest.fixture
def authenticated_client(client):
    # Replace with test credentials or mock
    auth_response = client.authenticate("test@example.com", "test_password")
    if not auth_response.success:
        pytest.skip("Authentication failed")
    return client 