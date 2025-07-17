# Helios Cinema Scraper

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

A Home Assistant custom integration that scrapes movie information from **any Helios Cinema location** in Poland.

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
