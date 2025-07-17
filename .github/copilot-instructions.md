# Helios Cinema Scraper Development Instructions

This is a Home Assistant custom integration that scrapes movie information from **any Helios Cinema location** in Poland and provides it as sensor data.

## Project Structure
- `custom_components/helios_cinema/` - Home Assistant integration files
- Web scraping logic uses aiohttp and BeautifulSoup4
- HACS-compatible integration structure

## Key Components
1. **Sensor** (`sensor.py`) - Fetches and parses movie data from configurable Helios website
2. **Integration** (`__init__.py`) - Home Assistant component setup with configurable cinema support
3. **Manifest** (`manifest.json`) - Integration metadata and dependencies

## Development Guidelines
- Follow Home Assistant development patterns and async/await usage
- Use proper error handling for web scraping (timeouts, HTTP errors)
- Implement proper integration lifecycle management
- Support multiple cinema locations through configuration
- Follow HACS integration requirements

## Web Scraping Notes
- Configurable cinema URL (default: https://helios.pl/wroclaw/kino-helios-magnolia)
- Works with any Helios cinema location in Poland
- Parse movie titles, descriptions, images, and showtimes
- Handle dynamic content and fallback parsing strategies
- Respect rate limiting and add appropriate delays

## Integration Behavior
- Creates sensor entity: `sensor.helios_cinema_{location_name}`
- State shows number of available movies
- Attributes contain complete movie data
- Configurable update intervals (default: 60 minutes)
- Unique entity naming per cinema location

## Configuration Options
- `cinema_url`: URL of the Helios cinema location
- `cinema_name`: Display name for the cinema
- `update_interval`: How often to fetch new data (minutes)

## HACS Integration
- Follows HACS integration requirements
- Uses `manifest.json` for dependencies
- Proper directory structure under `custom_components/`
- Compatible with Home Assistant 2023.1.0+
