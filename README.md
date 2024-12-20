# Haven Lighting API Client

A Python client library for interacting with the Haven Lighting API.

## Installation

```bash
pip install havenlighting
```

## Usage

```python
from havenlighting import HavenClient

# Initialize the client
client = HavenClient()

# Authenticate
authenticated = client.authenticate(
    email="your-email@example.com",
    password="your-password"
)

if authenticated:
    # Discover locations
    locations = client.discover_locations()
    
    # Print available locations and lights
    for location_id, location in locations.items():
        print(f"Location: {location.name}")
        
        # Get lights for this location
        lights = location.get_lights()
        
        # Control lights
        for light_id, light in lights.items():
            print(f"Light: {light.name}")
            light.turn_on()   # Turn light on
            light.turn_off()  # Turn light off

```

## Development

1. Clone the repository
2. Copy .env.example to .env and fill in your credentials:
```bash
cp .env.example .env
```
3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

## License

MIT License - see LICENSE file for details.