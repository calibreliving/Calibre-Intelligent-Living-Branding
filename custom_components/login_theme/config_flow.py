"""Config flow for Calibre Intelligent Living Branding."""

from __future__ import annotations

from typing import Any

try:  # Home Assistant 2026+ validates flow forms with probatio.
    import probatio as vol
except ImportError:  # pragma: no cover - older releases
    import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_SET_DEFAULT_THEME, DOMAIN

TITLE = "Calibre Intelligent Living"


class CalibreBrandingConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single step: optionally make Calibre the default theme."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the entry once the user confirms."""
        if user_input is not None:
            return self.async_create_entry(
                title=TITLE,
                data={CONF_SET_DEFAULT_THEME: bool(user_input.get(CONF_SET_DEFAULT_THEME))},
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Optional(CONF_SET_DEFAULT_THEME, default=True): bool}
            ),
        )
