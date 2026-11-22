(function () {
  // Run once per page even if a standalone copy is still registered.
  if (window.__calibreSidebarBranding) return;
  window.__calibreSidebarBranding = true;

  function deepQuery(root, selector) {
    let found;
    try {
      found = root.querySelector(selector);
    } catch (e) {}
    if (found) return found;
    const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (const el of all) {
      if (el.shadowRoot) {
        found = deepQuery(el.shadowRoot, selector);
        if (found) return found;
      }
    }
    return null;
  }

  function findByText(node, text) {
    if (node.nodeType === 3 && node.textContent.trim() === text) {
      return node.parentElement;
    }
    const children = node.childNodes || [];
    for (const child of children) {
      const r = findByText(child, text);
      if (r) return r;
    }
    if (node.shadowRoot) {
      const r = findByText(node.shadowRoot, text);
      if (r) return r;
    }
    return null;
  }

  let titleElRef = null;
  let line1Ref = null;
  let line2Ref = null;
  let overlayRef = null;
  let svgPath30Ref = null;

  // Read the theme's actual live CSS values rather than hardcoding hex
  // colors — this way the injected elements automatically match whichever
  // mode (light/dark) is actually active instead of only looking right in
  // the one mode they were written against.
  function themeVar(name, fallback) {
    const val = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return val || fallback;
  }

  function isDark(colorStr) {
    let r, g, b;
    const m = colorStr.match(/rgba?\(\s*(\d+),\s*(\d+),\s*(\d+)/i);
    if (m) {
      r = +m[1];
      g = +m[2];
      b = +m[3];
    } else {
      const hex = colorStr.replace('#', '');
      if (hex.length !== 6) return true;
      r = parseInt(hex.substr(0, 2), 16);
      g = parseInt(hex.substr(2, 2), 16);
      b = parseInt(hex.substr(4, 2), 16);
    }
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.5;
  }

  const GOLD = '#C5A059';
  const NAVY = '#0B1526';

  // Inlined so this script has zero external asset dependencies — HACS
  // "plugin" repos only manage the one JS file they're told about, not
  // companion files, so shipping the mark as a string keeps this a single
  // self-contained file.
  const MARK_SVG =
    '<svg viewBox="0 0 4619.1553 5072.0562" xmlns="http://www.w3.org/2000/svg">' +
    '<g transform="translate(-3173.1134,-1301.3053)">' +
    '<path d="m 0,0 c 1.299,3.927 -4,8.677 -4,10 v 76 c 0,13.298 -52.75,2.105 -61.835,1.835 C -138.403,85.677 -211.443,89.78 -284,88 V -4 h -80 v -84 h -84 v -84 h -140 v -612 h 92 v 228 h 64 L -432.021,-784.021 -384,-784 v 228 h 62 c 0.424,0 6,-5.576 6,-6 v -222 l 44.021,-0.021 L -276,-556 h 64 l 3.979,-228.021 L -164,-784 v 232 h 62 c 0.424,0 6,-5.576 6,-6 v -226 h 40 v 232 H 6 c 4.38,0 5.73,-9.765 6.204,-13.796 5.854,-49.871 -1.894,-117.442 -4.369,-168.04 -0.813,-16.627 0.917,-33.577 0.144,-50.185 L 52,-784 v 232 h 62 c 0.424,0 6,-5.576 6,-6 v -226 h 44 v 232 h 68 v -232 h 84 c -3.404,90.424 4.498,184.078 0.165,274.165 -1.745,36.276 -11.695,76.05 -12.358,111.643 -0.615,33.002 6.782,67.163 8.358,100.027 2.074,43.237 2.604,86.92 3.835,130.165 H 180 l 4,84 H 104 V 0 Z M -6,2836 3.976,411.979 151.462,407.476 c 4.84,-56.518 34.03,-66.053 84.111,-75.893 7.407,-31.877 -2.904,-112.405 33.52,-124.49 30.599,-12.752 229.647,-0.918 238.343,-11.661 l 4.585,-1155.453 -1288.042,-4 L -780,188 h 250 c 0.424,0 6,5.576 6,6 v 128 c 0,15.155 226.608,76.837 252,96 v 2418 z" style="fill:#C5A059" transform="matrix(1.3333333,0,0,-1.3333333,5690.6667,5088)" />' +
    '<path d="m 0,0 v -256 h -1072 c 0.83,-59.308 -1.045,-118.817 -0.165,-178.165 2.414,-162.773 4.682,-324.925 4.33,-488 -0.722,-334.273 -13,-682.225 -0.33,-1016 11.444,-301.468 114.705,-515.522 361.28,-690.72 86.622,-61.546 183.438,-105.391 276.908,-155.092 l 5.952,-300.006 c -158.296,62.528 -313.82,134.518 -453.239,232.718 -266.399,187.639 -453.036,472.816 -470.901,805.1 l 0.144,2042.186 z" style="fill:#C5A059" transform="matrix(1.3333333,0,0,-1.3333333,4970.6667,1301.3333)" />' +
    '<path d="m 0,0 1304.021,0.021 c 3.02,-112.662 2.149,-225.449 3.814,-338.186 7.528,-509.677 4.914,-1021.901 8.33,-1531.67 3.147,-469.504 -196.572,-798.48 -593.477,-1038.853 l -270.667,-143.292 -10.127,304.03 c 212.281,117.916 454.389,273.972 545.17,510.886 30.354,79.215 42.519,162.621 49.101,246.899 L 1036,-256 H 0 Z" style="fill:#C5A059" transform="matrix(1.3333333,0,0,-1.3333333,6037.3333,1301.3333)" />' +
    '<path d="m 0,0 c -1.611,5.205 -9.104,5.653 -13.796,6.204 -55.405,6.503 -143.548,0.085 -200.246,-4.162 -12.312,-0.922 -49.685,4.752 -53.399,-6.601 -2.011,-165.174 0.687,-330.417 -0.394,-495.606 -1.203,-183.956 -2.8,-367.575 0,-551.67 1.085,-71.372 -8.616,-168.544 0.174,-235.826 12.183,-93.258 175.725,-174.929 263.682,-162.36 l 3.958,336.042 276.042,-4 7.996,-446.038 c -1.194,-9.97 -12.051,-12.148 -20.097,-15.903 -80.763,-37.689 -197.483,-80.195 -282.92,-109.08 -110.823,-37.468 -176.717,-40.18 -280.679,21.32 -177.519,105.014 -243.395,301.526 -248.512,499.49 15.689,452.188 -20.202,917.737 0,1368.38 0.914,20.371 7.155,40.614 4.17,61.83 l 808.042,0.001 4,-648.042 L 0,-390 Z" style="fill:#C5A059" transform="matrix(1.3333333,0,0,-1.3333333,4613.3333,2328)" />' +
    '<path d="m 0,0 -3.442,-1661.444 c 6.48,-19.715 81.453,7.415 96.873,14.013 240.027,102.698 143.9,440.658 166.37,645.63 -1.558,5.083 6.949,17.801 10.199,17.801 h 240 c 4.38,0 5.73,-9.766 6.204,-13.796 8.569,-73.017 -0.706,-179.187 -0.369,-256.369 0.589,-134.89 14.847,-263.576 -39.114,-392.556 -50.638,-121.039 -219.552,-291.63 -358.666,-293.58 -65.617,-0.92 -277.882,91.006 -344.761,123.595 -10.028,4.887 -45.294,19.401 -45.294,30.706 V 0 Z" style="fill:#C5A059" transform="matrix(1.3333333,0,0,-1.3333333,6394.6667,1994.6667)" />' +
    '<path id="calibre-cutout" d="m 0,0 h 104 v -84 h 80 l -4,-84 h 136 c -1.231,-43.245 -1.761,-86.928 -3.835,-130.165 -1.576,-32.864 -8.973,-67.025 -8.358,-100.027 0.663,-35.593 10.613,-75.367 12.358,-111.643 C 320.498,-599.922 312.596,-693.576 316,-784 h -84 v 232 h -68 v -232 h -44 v 226 c 0,0.424 -5.576,6 -6,6 H 52 v -232 l -44.021,-0.021 c 0.773,16.608 -0.957,33.558 -0.144,50.185 2.475,50.598 10.223,118.169 4.369,168.04 C 11.73,-561.765 10.38,-552 6,-552 h -62 v -232 h -40 v 226 c 0,0.424 -5.576,6 -6,6 h -62 v -232 l -44.021,-0.021 L -212,-556 h -64 l 4.021,-228.021 L -316,-784 v 222 c 0,0.424 -5.576,6 -6,6 h -62 v -228 l -48.021,-0.021 L -432,-556 h -64 v -228 h -92 v 612 h 140 v 84 h 84 v 84 h 80 v 92 c 72.557,1.78 145.597,-2.323 218.165,-0.165 C -56.75,88.105 -4,99.298 -4,86 V 10 C -4,8.677 1.299,3.927 0,0" style="fill:#0B1526" transform="matrix(1.3333333,0,0,-1.3333333,5690.6667,5088)" />' +
    '</g></svg>';

  function syncColors() {
    const sidebarBg = themeVar('--sidebar-background-color', NAVY);
    const dark = isDark(sidebarBg);
    if (line1Ref) {
      line1Ref.style.color = dark ? GOLD : NAVY;
      // Cinzel's fine serif strokes render great at gold-on-navy but turn
      // jagged/hard to read as thin dark-on-light strokes at this size —
      // fall back to Montserrat (matching the subtitle) in light mode.
      line1Ref.style.fontFamily = dark ? '"Cinzel", serif' : '"Montserrat", sans-serif';
      line1Ref.style.letterSpacing = dark ? '2px' : '1.5px';
    }
    if (line2Ref) line2Ref.style.color = themeVar('--sidebar-text-color', dark ? '#EAE4D9' : '#5B6577');
    if (overlayRef) overlayRef.style.backgroundColor = sidebarBg;
    if (svgPath30Ref) svgPath30Ref.style.fill = sidebarBg;
  }

  function applyLogo() {
    const titleEl =
      deepQuery(document, '.menu .title') || findByText(document, 'Home Assistant');
    if (!titleEl) return false;
    titleElRef = titleEl;
    if (titleEl.dataset && titleEl.dataset.calibreLogoApplied) return true;
    if (titleEl.dataset) titleEl.dataset.calibreLogoApplied = 'true';

    titleEl.textContent = '';
    titleEl.style.color = '';
    titleEl.style.backgroundImage = 'none';
    titleEl.style.display = 'flex';
    titleEl.style.flexDirection = 'column';
    titleEl.style.justifyContent = 'center';
    titleEl.style.lineHeight = '1.15';
    titleEl.style.height = '40px';
    titleEl.style.width = '100%';
    titleEl.style.overflow = 'hidden';

    if (!document.getElementById('calibre-font-link')) {
      const fontLink = document.createElement('link');
      fontLink.id = 'calibre-font-link';
      fontLink.rel = 'stylesheet';
      fontLink.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap';
      document.head.appendChild(fontLink);
    }

    const line1 = document.createElement('div');
    line1.textContent = 'CALIBRE';
    line1.style.fontFamily = '"Cinzel", serif';
    line1.style.fontWeight = '700';
    line1.style.fontSize = '14px';
    line1.style.letterSpacing = '2px';
    line1.style.whiteSpace = 'nowrap';

    const line2 = document.createElement('div');
    line2.textContent = 'INTELLIGENT LIVING';
    line2.style.fontWeight = '500';
    line2.style.fontSize = '9px';
    line2.style.letterSpacing = '0.8px';
    line2.style.whiteSpace = 'nowrap';

    titleEl.appendChild(line1);
    titleEl.appendChild(line2);
    line1Ref = line1;
    line2Ref = line2;
    return true;
  }

  function applyMenuIcon() {
    const btn =
      deepQuery(document, 'button[aria-label="Sidebar Toggle"]') ||
      deepQuery(document, 'button[aria-label="Sidebar toggle"]') ||
      deepQuery(document, '[aria-label="Sidebar Toggle"]') ||
      deepQuery(document, '[aria-label="Sidebar toggle"]');
    if (!btn) return false;
    if (titleElRef && (btn === titleElRef || btn.contains(titleElRef))) return false;
    if (btn.dataset && btn.dataset.calibreIconApplied) return true;
    if (btn.dataset) btn.dataset.calibreIconApplied = 'true';

    if (getComputedStyle(btn).position === 'static') {
      btn.style.position = 'relative';
    }
    btn.style.overflow = 'hidden';

    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.inset = '0';
    overlay.style.zIndex = '2147483647';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.pointerEvents = 'none';
    btn.appendChild(overlay);
    overlayRef = overlay;

    const holder = document.createElement('div');
    holder.style.width = '65%';
    holder.style.height = '65%';
    overlay.appendChild(holder);

    holder.innerHTML = MARK_SVG;
    const svgEl = holder.querySelector('svg');
    if (svgEl) {
      svgEl.style.width = '100%';
      svgEl.style.height = '100%';
    }
    svgPath30Ref = holder.querySelector('#calibre-cutout');
    syncColors();

    return true;
  }

  function applyAll() {
    const a = applyLogo();
    const b = applyMenuIcon();
    syncColors();
    return a && b;
  }

  applyAll();
  const observer = new MutationObserver(() => {
    applyAll();
  });
  observer.observe(document.body, { childList: true, subtree: true });

  let tries = 0;
  const setupInterval = setInterval(() => {
    tries++;
    if (applyAll() || tries > 40) clearInterval(setupInterval);
  }, 500);

  // Keep re-syncing colors indefinitely so switching Light/Dark/Auto live
  // (no page reload) updates these injected elements too, not just a
  // hard refresh.
  setInterval(syncColors, 1000);
})();
