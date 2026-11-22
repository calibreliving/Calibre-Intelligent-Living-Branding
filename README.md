# Calibre Intelligent Living

One Home Assistant integration for all Calibre Intelligent Living theming and
branding. Install it once and you get:

- **The Calibre Intelligent Living theme**, light and dark mode. It's bundled,
  so no `themes/` file is needed.
- **Sidebar branding.** The "Home Assistant" sidebar title becomes the Calibre
  wordmark and the menu icon becomes the Calibre shield. Both follow light and
  dark mode.
- **A themed login page.** The login page loads before anyone signs in, so
  themes and frontend plugins never reach it. The integration themes it from
  inside Home Assistant: Calibre colours, the shield and wordmark in place of
  the Home Assistant logo, and a gold Log in button. This works on local
  connections, remote access (Cloudflare Tunnel, Nabu Casa) and the companion
  apps.
- **Its own icon and logo** on the Settings → Devices & Services page.

No `configuration.yaml` changes are needed.

## Installation via HACS

1. HACS → the three-dot menu (top right) → **Custom repositories**
2. Repository: `https://github.com/calibreliving/Calibre-Intelligent-Living-Branding`
   Category: **Integration**
3. Find **Calibre Intelligent Living** in HACS and click **Download**
4. Restart Home Assistant
5. **Settings → Devices & Services → Add Integration**, search for
   **Calibre Intelligent Living** and click **Submit**. Leave
   "Make Calibre Intelligent Living the default theme" ticked to switch every
   user who hasn't picked their own theme to Calibre.
6. Refresh the browser. Sign out, or open a private window, to see the login
   page.

### Manual installation

Copy `custom_components/login_theme` into `/config/custom_components/`, so
you end up with `/config/custom_components/login_theme/__init__.py`, then
follow steps 4–6 above.

## Upgrading from the separate theme and sidebar script

Earlier versions shipped the sidebar script as a HACS **Dashboard** download
plus a `frontend.extra_module_url` line, and the theme as a file in
`themes/`. The integration replaces all three:

- It takes over from the old `extra_module_url` line automatically, so the
  sidebar script never loads twice. You can delete the line whenever it suits
  you.
- Its bundled theme replaces a `themes/` file named
  `Calibre Intelligent Living`. You can delete that file.
- Remove the old **Dashboard** download in HACS. That also removes its
  dashboard resource.

## How it works

- **Theme.** Home Assistant only reads themes from `configuration.yaml`, so
  the integration adds the theme to the frontend directly and adds it back
  after **Reload themes**. If Calibre was saved as the default theme, it stays
  the default across restarts.
- **Sidebar.** The integration serves the script from
  `/calibre_branding/calibre-sidebar-branding.js` and registers it with the
  frontend, the same as an `extra_module_url` line would.
- **Login page.** The integration wraps the `/auth/authorize` route and adds
  the theme's colours for light and dark mode, plus the Calibre logo. If
  anything goes wrong while building the page, the stock login page is served
  instead, so it can never lock you out.

Removing the integration undoes all of it immediately.
