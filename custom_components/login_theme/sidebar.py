"""Serve the bundled sidebar branding script and load it on every page."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DATA_EXTRA_MODULE_URL, DOMAIN, SIDEBAR_JS, URL_BASE, VERSION

_LOGGER = logging.getLogger(__name__)

_STATIC_REGISTERED = f"{DOMAIN}_static_registered"


async def async_register_static(hass: HomeAssistant) -> None:
    """Serve the integration's frontend/ folder at URL_BASE (once per HA run)."""
    # Routes can't be removed, so a reload of the entry must not register again.
    if hass.data.get(_STATIC_REGISTERED):
        return
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(Path(__file__).parent / "frontend"), False)]
    )
    hass.data[_STATIC_REGISTERED] = True


def add_sidebar_script(hass: HomeAssistant) -> tuple[str, list[str]]:
    """Load the sidebar script on every page, replacing a standalone copy.

    Returns our URL and the standalone URLs we took over, so unload can put
    them back. The standalone copy comes from the old Dashboard install's
    frontend.extra_module_url line; leaving it would load the script twice.
    """
    url = f"{URL_BASE}/{SIDEBAR_JS}?v={VERSION}"
    manager = hass.data.get(DATA_EXTRA_MODULE_URL)
    current = manager.urls if manager is not None else frozenset()
    superseded = [u for u in current if SIDEBAR_JS in u and not u.startswith(URL_BASE)]
    for old in superseded:
        _LOGGER.info(
            "Replacing standalone sidebar script %s with the bundled one; the "
            "frontend.extra_module_url line for it can be removed",
            old,
        )
        remove_extra_js_url(hass, old)
    if url not in current:
        add_extra_js_url(hass, url)
    return url, superseded


def remove_sidebar_script(hass: HomeAssistant, url: str, superseded: list[str]) -> None:
    """Stop loading our script and restore any standalone copy we replaced."""
    remove_extra_js_url(hass, url)
    for old in superseded:
        add_extra_js_url(hass, old)
