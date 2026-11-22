"""Provide the bundled Calibre theme to the frontend.

Home Assistant only loads themes from configuration.yaml (usually the themes/
folder) and has no API for an integration to add one. We add it to the
frontend's theme table directly and put it back whenever themes are reloaded.
The bundled copy replaces a themes/ file of the same name, so the integration
is the single source of the Calibre theme.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant

from .const import (
    DATA_DEFAULT_DARK_THEME,
    DATA_DEFAULT_THEME,
    DATA_THEMES,
    DATA_THEMES_STORE,
    EVENT_THEMES_UPDATED,
)
from .theme import CALIBRE_THEME, THEME_NAME

_LOGGER = logging.getLogger(__name__)


class ThemeManager:
    """Keep the Calibre theme in the frontend's theme table."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.hass = hass
        self._replaced: Any = None
        self._unsub: CALLBACK_TYPE | None = None

    async def async_start(self) -> None:
        """Add the theme and keep it there across theme reloads."""
        await self._async_ensure()
        self._unsub = self.hass.bus.async_listen(EVENT_THEMES_UPDATED, self._async_on_update)

    async def async_stop(self) -> None:
        """Remove the theme, restoring a themes/ copy if we replaced one."""
        if self._unsub:
            self._unsub()
            self._unsub = None
        themes = self.hass.data.get(DATA_THEMES)
        if themes is None or themes.get(THEME_NAME) is not CALIBRE_THEME:
            return
        if self._replaced is not None:
            themes[THEME_NAME] = self._replaced
        else:
            del themes[THEME_NAME]
            for key, fallback in ((DATA_DEFAULT_THEME, "default"), (DATA_DEFAULT_DARK_THEME, None)):
                if self.hass.data.get(key) == THEME_NAME:
                    self.hass.data[key] = fallback
        self.hass.bus.async_fire(EVENT_THEMES_UPDATED)

    async def async_set_as_default(self) -> None:
        """Make Calibre the default theme for light and dark mode."""
        await self.hass.services.async_call(
            "frontend",
            "set_theme",
            {"name": THEME_NAME, "name_dark": THEME_NAME},
            blocking=True,
        )

    async def _async_on_update(self, event: Event) -> None:
        await self._async_ensure()

    async def _async_ensure(self) -> None:
        """Put our theme in place and restore a saved default that pointed at it."""
        themes = self.hass.data.get(DATA_THEMES)
        if themes is None:
            _LOGGER.warning("Frontend themes not loaded; Calibre theme not added")
            return
        changed = False
        current = themes.get(THEME_NAME)
        if current is not CALIBRE_THEME:
            if current is not None:
                _LOGGER.debug("Replacing the themes/ copy of %s with the bundled one", THEME_NAME)
            self._replaced = current
            themes[THEME_NAME] = CALIBRE_THEME
            changed = True
        changed |= await self._async_restore_defaults()
        # Our own event re-enters here, finds nothing to change, and stops.
        if changed:
            self.hass.bus.async_fire(EVENT_THEMES_UPDATED)

    async def _async_restore_defaults(self) -> bool:
        """Undo the frontend's reset of a saved Calibre default.

        At startup and on theme reload the frontend resets the default theme
        to "default" when the saved one isn't in its table yet, which is the
        case for a theme only this integration provides. The saved choice is
        still in the store, so put it back.
        """
        store = self.hass.data.get(DATA_THEMES_STORE)
        if store is None:
            return False
        saved = await store.async_load() or {}
        changed = False
        for key in (DATA_DEFAULT_THEME, DATA_DEFAULT_DARK_THEME):
            if saved.get(key) == THEME_NAME and self.hass.data.get(key) != THEME_NAME:
                self.hass.data[key] = THEME_NAME
                changed = True
        return changed
