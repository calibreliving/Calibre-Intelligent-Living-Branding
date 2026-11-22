"""Theme the Home Assistant login page.

The login page (/auth/authorize) is a static file served before anyone is
signed in, so the frontend never applies themes to it. We wrap that one route
and inject the default theme's CSS variables (light and dark mode) plus the
Calibre logo into the page. Because it runs inside Home Assistant, it applies
to every connection: local, Cloudflare Tunnel, and the companion apps.

If anything goes wrong while building the page, the stock login page is
served instead, so this can never lock you out.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
import logging
from pathlib import Path
import re
from typing import Any

from aiohttp import web

from homeassistant.core import HomeAssistant

from .branding import MARK_SVG
from .const import (
    BRAND_CREAM,
    BRAND_GOLD,
    BRAND_NAVY,
    BRAND_SLATE,
    DATA_DEFAULT_DARK_THEME,
    DATA_DEFAULT_THEME,
    DATA_THEMES,
    FONTS_URL,
    LOGIN_PATH,
)

_LOGGER = logging.getLogger(__name__)

Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]
type PatchedRoutes = list[tuple[Any, Handler]]

_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_LOGO_RE = re.compile(r"<img[^>]*favicon-192x192[^>]*>", re.IGNORECASE)

BRAND_HTML = (
    f"{MARK_SVG}"
    '<div class="lt-wordmark">'
    '<div class="lt-word1">CALIBRE</div>'
    '<div class="lt-word2">INTELLIGENT LIVING</div>'
    "</div>"
)


def patch_login_page(hass: HomeAssistant) -> PatchedRoutes:
    """Wrap the login page route; returns what to pass to restore_login_page."""
    patched: PatchedRoutes = []
    for route in hass.http.app.router.routes():
        resource = route.resource
        if (
            route.method != "GET"
            or resource is None
            or resource.canonical != LOGIN_PATH
        ):
            continue
        original: Handler = route._handler  # noqa: SLF001
        # Unwrap a leftover wrapper from an earlier load of this integration.
        original = getattr(original, "login_theme_original", original)
        route._handler = _make_handler(hass, original)  # noqa: SLF001
        patched.append((route, original))

    if not patched:
        _LOGGER.error("Could not find the %s route; login page left unchanged", LOGIN_PATH)
    return patched


def restore_login_page(patched: PatchedRoutes) -> None:
    """Put the original login page handler back."""
    for route, original in patched:
        route._handler = original  # noqa: SLF001


def _make_handler(hass: HomeAssistant, original: Handler) -> Handler:
    """Build the replacement handler for the login page."""
    # HA registers the page as partial(_serve_file, "<path>/authorize.html").
    args = getattr(original, "args", ())
    html_path = Path(args[0]) if args else None

    async def themed_login(request: web.Request) -> web.StreamResponse:
        try:
            path = html_path or await hass.async_add_executor_job(_frontend_login_path)
            html = await hass.async_add_executor_job(path.read_text, "utf-8")
            body = _inject(html, _build_head(hass))
        except Exception:
            _LOGGER.exception("Failed to theme the login page; serving the stock page")
            return await original(request)
        return web.Response(
            text=body,
            content_type="text/html",
            headers={"Cache-Control": "no-cache"},
        )

    themed_login.login_theme_original = original  # type: ignore[attr-defined]
    return themed_login


def _frontend_login_path() -> Path:
    import hass_frontend  # noqa: PLC0415

    return Path(hass_frontend.where()) / "authorize.html"


def _inject(html: str, head: str) -> str:
    """Add our styles at the end of <head> and swap the HA logo for Calibre's."""
    if "</head>" not in html:
        raise ValueError("login page has no </head>")
    html = html.replace("</head>", f"{head}</head>", 1)
    return _LOGO_RE.sub(BRAND_HTML, html, count=1)


def _theme_vars(hass: HomeAssistant, name: str | None, dark: bool) -> dict[str, str]:
    """Merge a theme's base variables with its light or dark mode, like the frontend does."""
    themes: dict[str, Any] = hass.data.get(DATA_THEMES) or {}
    theme = themes.get(name) if name else None
    if not isinstance(theme, dict):
        return {}
    merged = {k: v for k, v in theme.items() if k != "modes"}
    modes = theme.get("modes")
    if isinstance(modes, dict):
        merged.update(modes.get("dark" if dark else "light") or {})
    return {str(k): str(v) for k, v in merged.items()}


def _hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lstrip("#")
    if len(value) in (3, 4):
        value = "".join(c * 2 for c in value[:3])
    if len(value) not in (6, 8):
        return None
    try:
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return None


def _is_dark(color: str | None, fallback: bool) -> bool:
    rgb = _hex_to_rgb(color) if color and color.strip().startswith("#") else None
    if rgb is None:
        return fallback
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.5


def _resolve(theme: dict[str, str], value: str | None) -> str | None:
    """Follow var(--x) references to other variables in the same theme."""
    for _ in range(5):
        match = re.fullmatch(r"\s*var\(--([\w-]+)(?:\s*,[^)]*)?\)\s*", value or "")
        if not match:
            break
        value = theme.get(match.group(1))
    return value


def _derived(theme: dict[str, str]) -> dict[str, str]:
    """Map the classic theme colours onto HA's newer control tokens.

    Buttons, checkboxes and text fields read --ha-color-* tokens that older
    themes don't set, so they stay HA blue/grey. Fill them from the theme's
    own colours; anything the theme does set wins.
    """
    on_primary = "#FFFFFF" if _is_dark(_resolve(theme, theme.get("primary-color")), True) else BRAND_NAVY
    derived = {
        "ha-color-fill-primary-loud-resting": "var(--primary-color)",
        "ha-color-fill-primary-loud-hover": "color-mix(in srgb, var(--primary-color) 88%, white)",
        "ha-color-fill-primary-loud-active": "color-mix(in srgb, var(--primary-color) 80%, black)",
        "ha-color-on-primary-loud": on_primary,
        "wa-color-brand-on-loud": on_primary,
        "ha-checkbox-checked-icon-color": on_primary,
        "ha-color-form-background": (
            "color-mix(in srgb, var(--primary-text-color) 6%, var(--card-background-color))"
        ),
        "ha-color-form-background-hover": (
            "color-mix(in srgb, var(--primary-text-color) 10%, var(--card-background-color))"
        ),
        "ha-color-border-neutral-loud": (
            "color-mix(in srgb, var(--primary-text-color) 35%, transparent)"
        ),
    }
    return {k: v for k, v in derived.items() if k not in theme}


def _declarations(theme: dict[str, str], dark_fallback: bool) -> str:
    """Turn theme variables into CSS declarations, adding rgb-* twins like the frontend."""
    lines: list[str] = [f"--{k}: {v} !important;" for k, v in _derived(theme).items()]
    for key, value in theme.items():
        if not _KEY_RE.match(key):
            continue
        # Theme values go inside a <style> block; drop anything that could escape it.
        value = re.sub(r"[<>{};]", "", value).strip()
        if not value:
            continue
        lines.append(f"--{key}: {value} !important;")
        rgb_key = f"rgb-{key}"
        if value.startswith("#") and rgb_key not in theme and (rgb := _hex_to_rgb(value)):
            lines.append(f"--{rgb_key}: {','.join(map(str, rgb))} !important;")

    dark_bg = _is_dark(theme.get("primary-background-color"), dark_fallback)
    lines.append(f"--lt-brand-text: {BRAND_GOLD if dark_bg else BRAND_NAVY};")
    lines.append(f"--lt-brand-subtext: {BRAND_CREAM if dark_bg else BRAND_SLATE};")
    return "\n    ".join(lines)


def _build_head(hass: HomeAssistant) -> str:
    light_name = hass.data.get(DATA_DEFAULT_THEME)
    dark_name = hass.data.get(DATA_DEFAULT_DARK_THEME) or light_name
    light = _theme_vars(hass, light_name, dark=False)
    dark = _theme_vars(hass, dark_name, dark=True)

    css = f"""
  html {{
    {_declarations(light, dark_fallback=False)}
  }}
  @media (prefers-color-scheme: dark) {{
    html {{
    {_declarations(dark, dark_fallback=True)}
    }}
  }}
  html, body {{
    background-color: var(--primary-background-color) !important;
    color: var(--primary-text-color) !important;
  }}
  /* HA's floating particles are hard-coded blue; tint them gold. */
  #particles {{ filter: grayscale(1) sepia(1) saturate(1.6); }}
  .header {{ flex-direction: column; gap: 14px; }}
  .lt-mark {{ height: 76px; width: auto; }}
  .lt-gold {{ fill: {BRAND_GOLD}; }}
  .lt-cutout {{ fill: var(--primary-background-color, {BRAND_NAVY}); }}
  .lt-wordmark {{ text-align: center; line-height: 1.2; }}
  .lt-word1 {{
    font-family: "Cinzel", serif; font-weight: 700; font-size: 24px;
    letter-spacing: 4px; color: var(--lt-brand-text);
  }}
  .lt-word2 {{
    font-family: "Montserrat", sans-serif; font-weight: 500; font-size: 11px;
    letter-spacing: 2.5px; color: var(--lt-brand-subtext);
  }}
"""
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="stylesheet" href="{FONTS_URL}">'
        f'<style id="login-theme">{css}</style>'
    )
