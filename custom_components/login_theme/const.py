"""Constants for Calibre Intelligent Living Branding."""

DOMAIN = "login_theme"
VERSION = "2.0.0"

LOGIN_PATH = "/auth/authorize"

# Where the bundled frontend files are served, and the sidebar script in it.
URL_BASE = "/calibre_branding"
SIDEBAR_JS = "calibre-sidebar-branding.js"

CONF_SET_DEFAULT_THEME = "set_default_theme"

# Keys the frontend integration uses in hass.data (see frontend/helpers.py).
DATA_THEMES = "frontend_themes"
DATA_THEMES_STORE = "frontend_themes_store"
DATA_DEFAULT_THEME = "frontend_default_theme"
DATA_DEFAULT_DARK_THEME = "frontend_default_dark_theme"
DATA_EXTRA_MODULE_URL = "frontend_extra_module_url"
EVENT_THEMES_UPDATED = "themes_updated"

# Calibre brand colours (from the Calibre sidebar branding plugin).
BRAND_GOLD = "#C5A059"
BRAND_NAVY = "#0B1526"
BRAND_CREAM = "#EAE4D9"
BRAND_SLATE = "#5B6577"

FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Cinzel:wght@700"
    "&family=Montserrat:wght@500&display=swap"
)
