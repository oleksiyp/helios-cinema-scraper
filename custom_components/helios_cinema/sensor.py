"""Helios Cinema sensor platform."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import async_timeout
from bs4 import BeautifulSoup
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
        return len(self._films) if self._films else 0

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
        """Fetch films from Helios website."""
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(30):
                    async with session.get(self._cinema_url) as response:
                        if response.status != 200:
                            _LOGGER.error(f"HTTP {response.status} error fetching {self._cinema_url}")
                            return []
                        
                        html = await response.text()
                        return self._parse_films(html)
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout fetching Helios Cinema data")
            return []
        except Exception as err:
            _LOGGER.error(f"Error fetching films: {err}")
            return []

    def _parse_films(self, html: str) -> list[dict[str, Any]]:
        """Parse films from HTML."""
        films = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to extract movie data from the JavaScript object
        films = self._extract_from_javascript(html)
        
        if films:
            _LOGGER.debug(f"Successfully extracted {len(films)} films from JavaScript data")
            return films
        
        # Fallback to HTML parsing if JavaScript extraction fails
        _LOGGER.debug("JavaScript extraction failed, trying HTML parsing")
        films = self._parse_html_structure(soup)
        
        return films

    def _extract_from_javascript(self, html: str) -> list[dict[str, Any]]:
        """Extract movie data from the JavaScript object in the page."""
        films = []
        
        try:
            # Look for the main data object in the script tag
            import re
            import json
            
            # Find the script with the large data object
            # The pattern looks like: window.__NUXT__=(function(...){ ... })(params)
            pattern = r'window\.__NUXT__=\(function[^}]+\}\)\(([^)]+)\);'
            match = re.search(pattern, html)
            
            if not match:
                _LOGGER.debug("Could not find __NUXT__ data object")
                return []
            
            # Extract the parameters passed to the function
            params_str = match.group(1)
            _LOGGER.debug(f"Found __NUXT__ parameters: {params_str[:200]}...")
            
            # Parse the parameters - they're comma-separated strings and values
            # This is a simplified approach - look for movie titles in the parameters
            movies_data = self._extract_movie_titles_from_params(params_str)
            
            for movie_title in movies_data:
                film = {
                    'title': movie_title,
                    'description': 'Extracted from JavaScript data',
                    'image': 'https://via.placeholder.com/300x450/cccccc/000000?text=Movie+Poster',
                    'showtimes_today': [],
                    'showtimes_tomorrow': []
                }
                films.append(film)
                
        except Exception as e:
            _LOGGER.debug(f"Error extracting from JavaScript: {e}")
            
        return films

    def _extract_movie_titles_from_params(self, params_str: str) -> list[str]:
        """Extract movie titles from the JavaScript parameters."""
        titles = []
        
        try:
            # Look for quoted strings that look like movie titles
            import re
            
            # Find quoted strings in the parameters
            quoted_strings = re.findall(r'"([^"]+)"', params_str)
            
            # Filter for likely movie titles (reasonable length, contains letters)
            for string in quoted_strings:
                if (10 <= len(string) <= 80 and 
                    any(c.isalpha() for c in string) and
                    not string.startswith('http') and
                    not string.startswith('/') and
                    not '.' in string[-5:] and  # Avoid file extensions
                    not string.lower() in ['dubbing', 'napisy', 'action', 'comedy'] and
                    ' ' in string):  # Movie titles usually have spaces
                    
                    # Additional filters for movie-like titles
                    if any(keyword in string.lower() for keyword in [
                        'superman', 'basia', 'film', 'movie', 'kino', 'maraton', 'harry potter'
                    ]):
                        if string not in titles:  # Avoid duplicates
                            titles.append(string)
            
        except Exception as e:
            _LOGGER.debug(f"Error parsing movie titles: {e}")
            
        return titles[:10]  # Limit to 10 movies

    def _parse_html_structure(self, soup) -> list[dict[str, Any]]:
        """Fallback HTML parsing method."""
        films = []
        
        # Look for film containers using various approaches
        film_containers = soup.find_all('div', class_=['movie-card', 'film-item', 'movie-item'])
        
        if not film_containers:
            # Try to find headings that might be movie titles
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings[:5]:  # Limit to first 5
                text = heading.get_text(strip=True)
                if text and 10 <= len(text) <= 80:
                    film = {
                        'title': text,
                        'description': 'Extracted from page headings',
                        'image': 'https://via.placeholder.com/300x450/cccccc/000000?text=Movie',
                        'showtimes_today': [],
                        'showtimes_tomorrow': []
                    }
                    films.append(film)
        
        return films

    def _extract_film_data(self, container) -> dict[str, Any] | None:
        """Extract film data from a container element."""
        film = {}
        
        # Try to find title
        title_elem = (
            container.find('h1') or 
            container.find('h2') or 
            container.find('h3') or
            container.find('h4') or
            container.find(class_=lambda x: x and 'title' in x.lower()) or
            container.find(class_=lambda x: x and 'name' in x.lower())
        )
        
        if title_elem:
            film['title'] = title_elem.get_text(strip=True)
        
        # Try to find image
        img_elem = container.find('img')
        if img_elem:
            img_src = img_elem.get('src') or img_elem.get('data-src')
            if img_src:
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    img_src = 'https://helios.pl' + img_src
                film['image'] = img_src
        
        # Try to find description
        desc_elem = (
            container.find(class_=lambda x: x and 'description' in x.lower()) or
            container.find(class_=lambda x: x and 'summary' in x.lower()) or
            container.find('p')
        )
        
        if desc_elem:
            film['description'] = desc_elem.get_text(strip=True)[:200] + "..."
        
        # Try to find showtimes
        showtimes = []
        time_elems = (
            container.find_all(class_=lambda x: x and any(term in x.lower() for term in ['time', 'hour', 'show'])) or
            container.find_all('span', string=lambda text: text and ':' in text and len(text) <= 10)
        )
        
        for time_elem in time_elems:
            time_text = time_elem.get_text(strip=True)
            if ':' in time_text and len(time_text) <= 10:
                showtimes.append(time_text)
        
        film['showtimes_today'] = showtimes[:5]  # Limit to 5 showtimes
        film['showtimes_tomorrow'] = []  # This would need more complex parsing
        
        return film if film.get('title') else None

    def _fallback_film_parsing(self, soup) -> list[dict[str, Any]]:
        """Fallback method to parse films when main method fails."""
        films = []
        
        # Look for any elements that might contain film titles
        potential_titles = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=True)
        
        for title_elem in potential_titles[:5]:  # Limit to 5
            title_text = title_elem.get_text(strip=True)
            if len(title_text) > 3 and len(title_text) < 100:  # Reasonable title length
                film = {
                    'title': title_text,
                    'description': 'No description available',
                    'image': 'https://via.placeholder.com/300x450/cccccc/000000?text=No+Image',
                    'showtimes_today': [],
                    'showtimes_tomorrow': []
                }
                films.append(film)
        
        return films
