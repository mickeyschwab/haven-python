import time
import logging
import os
from havenlighting import HavenClient

def main():
    # Initialize client with debug logging
    client = HavenClient(log_level=logging.DEBUG)
    
    # Get credentials from environment variables
    email = os.getenv("HAVEN_EMAIL")
    password = os.getenv("HAVEN_PASSWORD")
    
    if not email or not password:
        print("Please set HAVEN_EMAIL and HAVEN_PASSWORD environment variables")
        return
    
    # Authenticate
    authenticated = client.authenticate(email=email, password=password)
    
    if not authenticated:
        print("Authentication failed")
        return

    # Discover locations
    print("\nDiscovering locations...")
    locations = client.discover_locations()

    # Print available locations and lights
    for location_id, location in locations.items():
        print(f"Location: {location.name}")
        lights = location.get_lights()
        
        for light_id, light in lights.items():
            print(f"  Light: {light.name}")
            light.turn_on()
            print("  Light turned on, waiting 5 seconds...")
            time.sleep(5)
            light.turn_off()
            print("  Light turned off")
            # Only control the first light
            break
        # Only process first location
        break

if __name__ == "__main__":
    main()