"""Calibre Intelligent Living Branding.

One integration for all Calibre theming and branding:
- the Calibre Intelligent Living theme (light and dark mode)
- the sidebar wordmark and shield menu icon
- a themed login page, for local and remote connections alike
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_SET_DEFAULT_THEME
from .login_page import PatchedRoutes, patch_login_page, restore_login_page
from .sidebar import add_sidebar_script, async_register_static, remove_sidebar_script
from .theme_manager import ThemeManager


@dataclass
class BrandingData:
    """What async_unload_entry needs to undo."""

    themes: ThemeManager
    sidebar_url: str
    superseded_urls: list[str]
    login_routes: PatchedRoutes


type BrandingConfigEntry = ConfigEntry[BrandingData]


async def async_setup_entry(hass: HomeAssistant, entry: BrandingConfigEntry) -> bool:
    """Apply the theme, sidebar branding and login page."""
    themes = ThemeManager(hass)
    await themes.async_start()
    if entry.data.get(CONF_SET_DEFAULT_THEME):
        await themes.async_set_as_default()
        # One-time choice from setup; later changes in the UI are the user's.
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_SET_DEFAULT_THEME: False}
        )

    await async_register_static(hass)
    sidebar_url, superseded = add_sidebar_script(hass)

    entry.runtime_data = BrandingData(
        themes=themes,
        sidebar_url=sidebar_url,
        superseded_urls=superseded,
        login_routes=patch_login_page(hass),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: BrandingConfigEntry) -> bool:
    """Undo everything async_setup_entry applied."""
    data = entry.runtime_data
    restore_login_page(data.login_routes)
    remove_sidebar_script(hass, data.sidebar_url, data.superseded_urls)
    await data.themes.async_stop()
    return True
