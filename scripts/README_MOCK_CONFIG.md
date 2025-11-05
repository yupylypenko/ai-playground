# Mock Configuration Generator

A script to generate realistic mock configuration data for the Cosmic Flight Simulator.

## Usage

### Basic Usage

```bash
# Generate default configuration (JSON)
python3 scripts/generate_mock_config.py

# Generate specific number of users and missions
python3 scripts/generate_mock_config.py --users 10 --missions 20

# Generate .env format
python3 scripts/generate_mock_config.py --format env -o config.env

# Generate both formats
python3 scripts/generate_mock_config.py --format both -o config
```

### Options

- `--output, -o`: Output file path (default: `mock_config.json`)
- `--format, -f`: Output format: `json`, `env`, or `both` (default: `json`)
- `--users`: Number of users to generate (default: 5)
- `--missions`: Number of missions to generate (default: 10)
- `--include`: What to include: `all`, `users`, `missions`, `system`, `spacecraft`, `game`, `mongodb` (default: `all`)

### Examples

```bash
# Generate only users and missions
python3 scripts/generate_mock_config.py --include users missions --users 5 --missions 10

# Generate only solar system configuration
python3 scripts/generate_mock_config.py --include system --format json -o solar_system.json

# Generate MongoDB configuration as .env
python3 scripts/generate_mock_config.py --include mongodb --format env -o .env.mongodb
```

## Generated Data

### Users
- User profiles with realistic statistics
- Display preferences (screen resolution, fonts, audio)
- Game progression (missions completed, achievements)
- Flight statistics (flight time, distance, fuel)

### Missions
- Multiple mission types (tutorial, free_flight, challenge)
- Difficulty levels (beginner, intermediate, advanced)
- Objectives with different types (reach, collect, maintain, avoid)
- Time limits and fuel constraints

### Solar System
- 9 celestial bodies (Sun, planets, moons)
- Realistic physical properties (mass, radius, temperature)
- Atmosphere and water information
- Accurate astronomical data

### Spacecraft
- 4 spacecraft types (Scout, Freighter, Fighter, Explorer)
- Realistic specifications (mass, thrust, fuel capacity)
- Performance characteristics (cruise speed, specific impulse)

### Game Configuration
- Default screen settings
- Physics constants
- Performance parameters

### MongoDB Configuration
- Connection settings
- Database name
- Authentication (optional)

## Output Formats

### JSON Format
Structured JSON data suitable for:
- Direct import into Python applications
- MongoDB seeding
- Configuration files
- API testing

### .env Format
Environment variable format suitable for:
- Docker configurations
- Environment variable loading
- CI/CD pipelines
- Local development setup

## Use Cases

1. **Development Testing**: Generate test data for development
2. **MongoDB Seeding**: Populate database with realistic data
3. **Integration Testing**: Create test scenarios
4. **Demo Data**: Generate data for demonstrations
5. **Performance Testing**: Generate large datasets for load testing

## Example Output

```json
{
  "users": [
    {
      "id": "user-630d9f94",
      "username": "space_pilot_01",
      "email": "space_pilot_01@spaceflight.example",
      "display_name": "Space Pilot 01",
      ...
    }
  ],
  "missions": [
    {
      "id": "mission-000",
      "name": "Tutorial: First Steps",
      "type": "tutorial",
      "difficulty": "beginner",
      ...
    }
  ],
  "solar_system": {
    "name": "Sol System",
    "bodies": [...]
  }
}
```

## Integration

### Loading into MongoDB

```python
from src.adapters import MongoDatabase
from src.cockpit.config import MongoConfig
import json

# Load generated config
with open('mock_config.json') as f:
    config = json.load(f)

# Connect to MongoDB
db = MongoDatabase(MongoConfig.from_env())
db.connect()

# Insert users
for user_data in config['users']:
    user = User(**user_data)
    db.user_repository.save_user(user)

# Insert missions
for mission_data in config['missions']:
    mission = Mission(**mission_data)
    db.mission_repository.save_mission(mission)
```

### Using .env Configuration

```bash
# Load environment variables
source mock_config.env

# Or use with docker-compose
docker-compose --env-file mock_config.env up
```

