"""The Calibre Intelligent Living theme, bundled so no themes/ file is needed."""

THEME_NAME = "Calibre Intelligent Living"

CALIBRE_THEME: dict = {
    # Brand palette
    "calibre-navy": "#0B1526",
    "calibre-navy-raised": "#13213A",
    "calibre-navy-line": "#22324F",
    "calibre-gold": "#C5A059",
    "calibre-cream": "#EAE4D9",
    # Shared across modes
    "primary-color": "var(--calibre-gold)",
    "accent-color": "var(--calibre-gold)",
    "state-icon-color": "var(--calibre-gold)",
    "app-header-selection-bar-color": "var(--calibre-gold)",
    "sidebar-selected-icon-color": "var(--calibre-gold)",
    # HA's newer controls (buttons, checkboxes) read these instead of
    # primary-color, so without them they stay HA blue.
    "ha-color-fill-primary-loud-resting": "var(--primary-color)",
    "ha-color-fill-primary-loud-hover": "color-mix(in srgb, var(--primary-color) 88%, white)",
    "ha-color-fill-primary-loud-active": "color-mix(in srgb, var(--primary-color) 80%, black)",
    "ha-color-on-primary-loud": "var(--calibre-navy)",
    "wa-color-brand-on-loud": "var(--calibre-navy)",
    "ha-checkbox-checked-icon-color": "var(--calibre-navy)",
    "modes": {
        "light": {
            "primary-background-color": "#F6F3EE",
            "secondary-background-color": "var(--calibre-cream)",
            "card-background-color": "#FFFFFF",
            "ha-card-background": "#FFFFFF",
            "divider-color": "#DDD5C7",
            "primary-text-color": "var(--calibre-navy)",
            "secondary-text-color": "#5B6577",
            "app-header-background-color": "#F6F3EE",
            "app-header-text-color": "var(--calibre-navy)",
            "sidebar-background-color": "var(--calibre-cream)",
            "sidebar-text-color": "#5B6577",
            "sidebar-icon-color": "#5B6577",
            "sidebar-selected-text-color": "var(--calibre-navy)",
        },
        "dark": {
            "primary-background-color": "var(--calibre-navy)",
            "secondary-background-color": "var(--calibre-navy-raised)",
            "card-background-color": "var(--calibre-navy-raised)",
            "ha-card-background": "var(--calibre-navy-raised)",
            "ha-card-border-color": "var(--calibre-navy-line)",
            "divider-color": "var(--calibre-navy-line)",
            "primary-text-color": "var(--calibre-cream)",
            "secondary-text-color": "#9AA3B5",
            "app-header-background-color": "var(--calibre-navy)",
            "app-header-text-color": "var(--calibre-cream)",
            "sidebar-background-color": "var(--calibre-navy)",
            "sidebar-text-color": "var(--calibre-cream)",
            "sidebar-icon-color": "#9AA3B5",
            "sidebar-selected-text-color": "var(--calibre-gold)",
            "sidebar-selected-background-color": "var(--calibre-navy-raised)",
        },
    },
}
