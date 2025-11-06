# Asteroid Data Scraper

A script to scrape real asteroid data from public HTML sources and save as structured files (CSV/JSON).

## Features

- ✅ Scrapes real asteroid data from NASA NEO API
- ✅ Parses HTML tables from public data sources
- ✅ Exports to CSV and JSON formats
- ✅ Handles errors gracefully with fallback data
- ✅ Configurable output and limits

## Installation

```bash
pip install beautifulsoup4 requests
```

## Usage

### Basic Usage

```bash
# Scrape asteroid data (default: 50 asteroids, both CSV and JSON)
python3 scripts/scrape_asteroid_data.py

# Limit number of asteroids
python3 scripts/scrape_asteroid_data.py --limit 20

# Output only CSV
python3 scripts/scrape_asteroid_data.py --format csv -o asteroids

# Output only JSON
python3 scripts/scrape_asteroid_data.py --format json -o asteroids

# Scrape from custom HTML URL
python3 scripts/scrape_asteroid_data.py --url https://example.com/asteroid-table.html
```

### Options

- `--output, -o`: Output file path (without extension, default: `asteroid_data`)
- `--format, -f`: Output format: `csv`, `json`, or `both` (default: `both`)
- `--limit, -l`: Maximum number of asteroids to retrieve (default: 50)
- `--url`: Custom HTML URL to scrape (optional)

## Data Sources

### Primary Source: NASA NEO API
- Uses NASA's Near Earth Object Web Service API
- Provides real-time asteroid data
- Includes diameter, velocity, distance, hazard status

### Fallback: HTML Table Scraping
- Can scrape from any HTML page with asteroid data tables
- Automatically detects table structure
- Parses headers and data rows

### Sample Data Generator
- Generates realistic sample data if API/scraping fails
- Useful for testing and development

## Output Format

### JSON Output
```json
{
  "metadata": {
    "source": "NASA NEO API / HTML Scraper",
    "generated_at": "2025-11-06T10:00:00",
    "count": 50
  },
  "asteroids": [
    {
      "id": "2138175",
      "name": "138175 (2000 EE104)",
      "diameter_min_km": 0.212,
      "diameter_max_km": 0.474,
      "is_hazardous": true,
      "close_approach_date": "2025-11-06",
      "relative_velocity_kmh": 22930.8,
      "miss_distance_km": 18284482.7,
      "orbital_period_days": 365.2
    }
  ]
}
```

### CSV Output
Standard CSV format with headers matching JSON fields.

## Example Output

```bash
$ python3 scripts/scrape_asteroid_data.py --limit 5

============================================================
Asteroid Data Scraper
============================================================

Fetching asteroid data...
  Using NASA NEO API...
✓ Retrieved 5 asteroids

✓ Saved 5 asteroids to CSV: asteroid_data.csv
✓ Saved 5 asteroids to JSON: asteroid_data.json

Sample asteroid data:
  id: 2138175
  name: 138175 (2000 EE104)
  diameter_min_km: 0.2121069879
  diameter_max_km: 0.4742856434
  is_hazardous: True
```

## Use Cases

1. **Space Simulation Data**: Import real asteroid data into the simulator
2. **Research**: Analyze asteroid characteristics and trajectories
3. **Testing**: Generate test data for space-related applications
4. **Education**: Learn about near-Earth objects and their properties

## Data Fields

- `id`: Unique asteroid identifier
- `name`: Asteroid name/designation
- `diameter_min_km`: Minimum estimated diameter in kilometers
- `diameter_max_km`: Maximum estimated diameter in kilometers
- `is_hazardous`: Whether asteroid is potentially hazardous
- `close_approach_date`: Date of closest approach to Earth
- `relative_velocity_kmh`: Relative velocity in km/h
- `miss_distance_km`: Closest approach distance in kilometers
- `orbital_period_days`: Orbital period in days

## Error Handling

The script includes robust error handling:
- API failures fall back to HTML scraping
- HTML scraping failures fall back to sample data generation
- All errors are logged with informative messages

## Integration

### Using in Python

```python
from scripts.scrape_asteroid_data import scrape_nasa_neo_data, save_as_json

# Scrape data
asteroids = scrape_nasa_neo_data(limit=100)

# Save to file
save_as_json(asteroids, Path("asteroids.json"))
```

### Using in MongoDB

```python
from src.adapters import MongoDatabase
from src.cockpit.config import MongoConfig
import json

# Load scraped data
with open('asteroid_data.json') as f:
    data = json.load(f)

# Store in MongoDB
config = MongoConfig.from_env()
with MongoDatabase(config) as db:
    collection = db.db.asteroids
    collection.insert_many(data['asteroids'])
```

## Notes

- NASA API uses a demo key by default (rate-limited)
- For production use, get a free API key from https://api.nasa.gov/
- HTML scraping respects robots.txt and includes proper User-Agent headers
- All data is publicly available and suitable for educational/research use

