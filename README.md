# Helios Cinema Scraper

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Helios Cinema Scraper

A Python package and Home Assistant custom component that scrapes movie information from **any Helios Cinema location** in Poland and provides it as sensor data.

## Project Structure

```
helios-cinema-scraper/
├── src/
│   └── helios_scraper/           # Main scraper package
│       ├── __init__.py
│       ├── scraper.py           # Core scraping logic
│       └── cli.py               # Command line interface
├── tests/
│   └── test_scraper.py          # Test suite
├── custom_components/
│   └── helios_cinema/           # Home Assistant integration
│       ├── __init__.py
│       ├── manifest.json
│       └── sensor.py
├── test_page.html               # Test data for offline testing
├── setup.py                     # Package installation
└── requirements.txt
```

## Features

- **Scrapes any Helios Cinema location** in Poland
- **Robust extraction** from modern NUXT/SPA websites
- **Multiple extraction strategies** (JavaScript data + HTML fallback)
- **Home Assistant integration** with configurable cinema locations
- **Command line interface** for standalone usage
- **Comprehensive test suite** with offline testing capability

## Installation

### For Development

```bash
git clone https://github.com/yourusername/helios-cinema-scraper.git
cd helios-cinema-scraper
pip install -r requirements.txt
```

### As a Package

```bash
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Scrape from live website
python3 -m src.helios_scraper.cli --url https://helios.pl/wroclaw/kino-helios-magnolia

# Extract from saved HTML file
python3 -m src.helios_scraper.cli --file test_page.html --limit 5

# JSON output
python3 -m src.helios_scraper.cli --file test_page.html --format json
```

### Python API

```python
import asyncio
from src.helios_scraper import HeliosScraper, extract_films_from_file

# Scrape from live website
async def main():
    scraper = HeliosScraper("https://helios.pl/wroclaw/kino-helios-magnolia")
    films = await scraper.get_films()
    print(f"Found {len(films)} films")

asyncio.run(main())

# Extract from HTML file
films = extract_films_from_file("test_page.html")
for film in films:
    print(f"Title: {film['title']}")
    print(f"Showtimes: {film['showtimes_today']}")
```

### Home Assistant Integration

1. Copy the `custom_components/helios_cinema` folder to your Home Assistant `custom_components` directory
2. Add to your `configuration.yaml`:

```yaml
helios_cinema:
  cinema_url: "https://helios.pl/wroclaw/kino-helios-magnolia"
  cinema_name: "Helios Magnolia"
  update_interval: 60  # minutes
```

3. Restart Home Assistant
4. The sensor `sensor.helios_cinema_films_magnolia` will be created

## Configuration Options

### Home Assistant

- `cinema_url`: URL of the Helios cinema location (required)
- `cinema_name`: Display name for the cinema (optional)
- `update_interval`: How often to fetch new data in minutes (default: 60)

### CLI Options

- `--url, -u`: Cinema URL to scrape
- `--file, -f`: Extract from HTML file instead of live URL
- `--timeout, -t`: Timeout for HTTP requests (seconds)
- `--format, -F`: Output format (json, text)
- `--limit, -l`: Limit number of films to show

## Supported Cinema Locations

Works with any Helios cinema in Poland. Common locations:

- `https://helios.pl/wroclaw/kino-helios-magnolia`
- `https://helios.pl/warszawa/kino-helios-city`
- `https://helios.pl/krakow/kino-helios-plaza`
- `https://helios.pl/gdansk/kino-helios-madison`

## Testing

```bash
# Run all tests
python3 tests/test_scraper.py

# Run tests with verbose output
python3 tests/test_scraper.py -v
```

## Technical Details

### Extraction Strategy

1. **NUXT/JavaScript Extraction**: Parses the `window.__NUXT__` data structure for movie titles and showtimes
2. **HTML Fallback**: If JavaScript extraction fails, falls back to HTML parsing
3. **Regex Patterns**: Uses targeted patterns to identify movie titles and showtime data
4. **Context-Aware Grouping**: Associates showtimes with their corresponding movies

### Data Structure

Each film contains:
- `title`: Movie title
- `description`: Brief description
- `image`: Poster image URL
- `showtimes_today`: List of today's showtimes (HH:MM format)
- `showtimes_tomorrow`: List of tomorrow's showtimes

### Error Handling

- Network timeouts and HTTP errors
- Invalid HTML structure
- Missing JavaScript data
- Malformed movie information

## Development

### Adding New Cinema Locations

The scraper automatically works with any Helios cinema URL. Simply change the URL in the configuration.

### Improving Extraction

To improve extraction accuracy:

1. Update the title patterns in `scraper.py`
2. Add new keyword filters for movie recognition
3. Enhance the showtime grouping logic
4. Add tests for new scenarios

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## HACS Integration

This integration is compatible with HACS (Home Assistant Community Store). To install via HACS:

1. Add this repository as a custom repository in HACS
2. Install the "Helios Cinema" integration
3. Configure via `configuration.yaml`
4. Restart Home Assistant

## Features

- 🎬 Fetch movie data from any Helios Cinema location
- 🔄 Configurable update intervals
- 🎯 Unique entity naming per cinema location
- 📊 Movie details including titles, descriptions, images, and showtimes
- 🛡️ Robust error handling and rate limiting

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=oleksiyp&repository=helios-cinema-scraper&category=integration)

1. Install [HACS](https://hacs.xyz/) if you haven't already
2. Add this repository as a custom repository in HACS
3. Install "Helios Cinema Scraper" through HACS
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/helios_cinema` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: helios_cinema
    cinema_url: "https://helios.pl/wroclaw/kino-helios-magnolia"
    cinema_name: "Wrocław Magnolia"
    update_interval: 60  # minutes (optional, default: 60)
```

### Available Cinema URLs

You can use any Helios Cinema location by changing the URL:

- **Wrocław Magnolia**: `https://helios.pl/wroclaw/kino-helios-magnolia`
- **Warszawa City**: `https://helios.pl/warszawa/kino-helios-city`
- **Kraków Plaza**: `https://helios.pl/krakow/kino-helios-plaza`
- **Gdańsk Madison**: `https://helios.pl/gdansk/kino-helios-madison`

Find your local cinema at [helios.pl](https://helios.pl) and use its URL.

## Entity Information

The integration creates a sensor entity with:
- **Entity ID**: `sensor.helios_cinema_{location_name}`
- **State**: Number of currently available movies
- **Attributes**: Complete movie data including titles, descriptions, images, and showtimes

## Usage with Frontend

This integration pairs perfectly with the [Helios Cinema Card](https://github.com/oleksiyp/helios-cinema-card) for displaying movie information in your Home Assistant dashboard.

## Support

If you find this integration helpful, consider supporting the development!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
