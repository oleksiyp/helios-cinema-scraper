"""Helios Cinema integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "helios_cinema"
PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("update_interval", default=30): cv.positive_int,
                vol.Optional("cinema_url", default="https://helios.pl/wroclaw/kino-helios-magnolia"): cv.string,
                vol.Optional("cinema_name", default="Helios Cinema"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Helios Cinema component."""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        hass.data[DOMAIN].update(config[DOMAIN])
    
    # Load the sensor platform using the proper discovery import
    await discovery.async_load_platform(hass, Platform.SENSOR, DOMAIN, {}, config)
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Helios Cinema from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
