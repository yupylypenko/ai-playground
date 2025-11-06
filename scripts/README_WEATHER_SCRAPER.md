# Weather Data Scraper

A script to scrape real-time weather data from public HTML sources and save as structured files.

## Features

- ✅ Scrapes real weather data from public HTML sources (wttr.in)
- ✅ Parses HTML tables from public weather websites
- ✅ Exports to CSV and JSON formats
- ✅ Supports multiple locations
- ✅ Robust error handling with fallback data generation
- ✅ Comprehensive documentation

## Installation

Dependencies are already in `requirements.txt`:
- `beautifulsoup4>=4.9.0` - HTML parsing
- `requests>=2.25.0` - HTTP requests

## Usage

### Basic Usage

```bash
# Scrape weather data for default location (London)
python3 scripts/scrape_weather_data.py

# Scrape for specific location
python3 scripts/scrape_weather_data.py --location "New York"

# Multiple locations
python3 scripts/scrape_weather_data.py --locations "London" "Paris" "Tokyo"

# Output only CSV
python3 scripts/scrape_weather_data.py --format csv -o weather

# Output only JSON
python3 scripts/scrape_weather_data.py --format json -o weather

# Scrape from custom HTML URL
python3 scripts/scrape_weather_data.py --url https://example.com/weather-table.html
```

### Options

- `--output, -o`: Output file path (without extension, default: `weather_data`)
- `--format, -f`: Output format: `csv`, `json`, or `both` (default: `both`)
- `--location, -l`: Location name for weather data (default: `London`)
- `--locations`: Multiple locations to fetch weather for
- `--url`: Custom HTML URL to scrape (optional)

## Data Sources

### Primary Source: wttr.in
- Public weather service providing HTML/JSON data
- No API key required
- Real-time weather data for cities worldwide

### Fallback: HTML Table Scraping
- Can scrape from any HTML page with weather data tables
- Automatically detects table structure
- Parses headers and data rows

### Sample Data Generator
- Generates realistic sample data if scraping fails
- Useful for testing and development

## Output Format

### JSON Output
```json
{
  "metadata": {
    "source": "Weather API / HTML Scraper",
    "generated_at": "2025-11-06T15:10:00",
    "count": 3
  },
  "weather": [
    {
      "location": "London",
      "country": "United Kingdom",
      "temperature_celsius": 12.5,
      "feels_like_celsius": 11.2,
      "humidity_percent": 65,
      "pressure_hpa": 1013,
      "wind_speed_ms": 5.2,
      "wind_direction_deg": 180,
      "cloudiness_percent": 75,
      "weather_description": "partly cloudy"
    }
  ]
}
```

### CSV Output
Standard CSV format with headers matching JSON fields.

## Data Fields

- `location`: City/location name
- `country`: Country name
- `temperature_celsius`: Temperature in Celsius
- `feels_like_celsius`: Feels-like temperature
- `humidity_percent`: Humidity percentage
- `pressure_hpa`: Atmospheric pressure in hPa
- `wind_speed_ms`: Wind speed in meters per second
- `wind_direction_deg`: Wind direction in degrees
- `cloudiness_percent`: Cloud cover percentage
- `visibility_km`: Visibility in kilometers
- `weather_description`: Weather condition description
- `precipitation_mm`: Precipitation in millimeters
- `timestamp`: Data collection timestamp

## Use Cases

1. **Weather Monitoring**: Track weather conditions for multiple locations
2. **Data Analysis**: Analyze weather patterns and trends
3. **Testing**: Generate test data for weather-related applications
4. **Integration**: Import weather data into other systems

## Example Output

```bash
$ python3 scripts/scrape_weather_data.py --locations "London" "Paris" "Tokyo"

============================================================
Weather Data Scraper
============================================================

Fetching weather data...
  Fetching weather for: London, Paris, Tokyo
  ✓ Fetched weather for London
  ✓ Fetched weather for Paris
  ✓ Fetched weather for Tokyo
✓ Retrieved 3 weather record(s)

✓ Saved 3 weather records to CSV: weather_data.csv
✓ Saved 3 weather records to JSON: weather_data.json
```

## Integration

### Using in Python

```python
from scripts.scrape_weather_data import scrape_public_weather_html, save_as_json

# Scrape data
weather = scrape_public_weather_html()

# Save to file
save_as_json(weather, Path("weather.json"))
```

### Using in MongoDB

```python
from src.adapters import MongoDatabase
from src.cockpit.config import MongoConfig
import json

# Load scraped data
with open('weather_data.json') as f:
    data = json.load(f)

# Store in MongoDB
config = MongoConfig.from_env()
with MongoDatabase(config) as db:
    collection = db.db.weather
    collection.insert_many(data['weather'])
```

## Notes

- Uses public weather services (no API key required)
- HTML scraping respects robots.txt and includes proper User-Agent headers
- All data is publicly available and suitable for educational/research use
- Fallback to sample data ensures script always produces output

