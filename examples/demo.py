import os
import time
from havenlighting import HavenLightingClient, AuthenticationError, ApiError

def main():
    # Get credentials from environment variables for security
    email =  os.getenv("HAVEN_EMAIL")
    password = os.getenv("HAVEN_PASSWORD")
    base_url = os.getenv("HAVEN_API_URL", "https://havenwebservices-apiapp-test.azurewebsites.net/api/v2")

    if not email or not password:
        print("Please set HAVEN_EMAIL and HAVEN_PASSWORD environment variables")
        return

    # Initialize client
    client = HavenLightingClient(base_url)
    
    try:
        # Authenticate
        print("Authenticating...")
        auth_response = client.authenticate(email, password)
        if not auth_response.success:
            print(f"Authentication failed: {auth_response.message}")
            return

        print("Successfully authenticated!")

        # Get locations
        print("\nFetching locations...")
        locations = client.locations.fetch_location_list()
        if not locations["data"]:
            print("No locations found")
            return

        # Get first location
        location = locations["data"][0]
        location_id = int(location["locationId"])
        print(f"Using location: {location['ownerName']} ({location_id})")

        # Get lights for location
        print("\nFetching lights...")
        lights_response = client.lights.fetch_location_lights_and_zones(location_id)
        if not lights_response["data"]["lights"]:
            print("No lights found")
            return

        # Get first light
        light = lights_response["data"]["lights"][0]
        light_id = light["lightId"]
        print(f"Using light: {light['name']} ({light_id})")

        # Control the light
        print("\nTurning light on...")
        response = client.lights.control_light(location_id, [light_id], turn_on=True)
        print("Success!" if response["success"] else "Failed to turn on light")

        # Wait a few seconds
        print("Waiting 5 seconds...")
        time.sleep(5)

        print("Turning light off...")
        response = client.lights.control_light(location_id, [light_id], turn_on=False)
        print("Success!" if response["success"] else "Failed to turn off light")

    except AuthenticationError as e:
        print(f"Authentication error: {e}")
    except ApiError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 