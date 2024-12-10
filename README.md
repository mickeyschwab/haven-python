# Haven Lighting API Client

A Python client library for interacting with the Haven Lighting API.

## Installation 
bash
pip install havenlighting
python
from havenlighting import HavenLightingClient

# Initialize the client
client = HavenLightingClient("https://api-base-url")
Authenticate
auth_response = client.authenticate("your-email@example.com", "your-password")
if auth_response.success:
# Get locations
locations = client.fetch_location_list()
# Control lights
if locations["success"] and locations["data"]:
location_id = locations["data"][0]["locationId"]
# Get lights for location
lights = client.fetch_location_lights_and_zones(location_id)
if lights["success"] and lights["data"]:
light_ids = [light["id"] for light in lights["data"]["lights"]]
# Turn lights on
client.control_light(location_id, light_ids, turn_on=True)
# Turn lights off
client.control_light(location_id, light_ids, turn_on=False)
3. Run tests: `pytest`