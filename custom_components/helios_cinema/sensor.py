"""Helios Cinema sensor platform."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .scraper import HeliosScraper
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Helios Cinema sensor platform."""
    cinema_config = hass.data.get("helios_cinema", {})
    cinema_url = cinema_config.get("cinema_url", "https://helios.pl/wroclaw/kino-helios-magnolia")
    update_interval = cinema_config.get("update_interval", 30)
    cinema_name = cinema_config.get("cinema_name", "Helios Cinema")
    
    sensor = HeliosCinemaSensor(cinema_url, update_interval, cinema_name)
    async_add_entities([sensor], True)


class HeliosCinemaSensor(SensorEntity):
    """Representation of a Helios Cinema sensor."""

    def __init__(self, cinema_url: str, update_interval: int, cinema_name: str) -> None:
        """Initialize the sensor."""
        self._cinema_url = cinema_url
        self._update_interval = update_interval
        self._cinema_name = cinema_name
        self._state = None
        self._films = []
        
        # Extract cinema location from URL for unique naming
        url_parts = cinema_url.split('/')
        location = "default"
        if len(url_parts) >= 4:
            location = url_parts[-2] if url_parts[-1] else url_parts[-2]
            if location.startswith('kino-'):
                location = location[5:]  # Remove 'kino-' prefix
        
        self._attr_name = f"{cinema_name} Films"
        self._attr_unique_id = f"helios_cinema_films_{location}"
        self._attr_icon = "mdi:movie"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        return str(len(self._films)) if self._films else "0"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "films": self._films,
            "last_updated": datetime.now().isoformat(),
            "cinema_url": self._cinema_url,
            "cinema_name": self._cinema_name,
        }

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self) -> None:
        """Update the sensor."""
        try:
            films = await self._fetch_films()
            self._films = films
            _LOGGER.debug(f"Updated films: {len(films)} films found")
        except Exception as err:
            _LOGGER.error(f"Error updating Helios Cinema data: {err}")
            self._films = []

    async def _fetch_films(self) -> list[dict[str, Any]]:
        """Fetch films from Helios website using the new scraper."""
        try:
            scraper = HeliosScraper(self._cinema_url, timeout=30)
            films = await scraper.get_films()
            _LOGGER.debug(f"Scraper found {len(films)} films")
            return films
        except Exception as err:
            _LOGGER.error(f"Error fetching films with scraper: {err}")
            return []


