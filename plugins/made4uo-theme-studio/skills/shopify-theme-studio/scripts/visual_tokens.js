(() => {
  const hex = (c) => {
    const m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const [r, g, b, a = 1] = m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);
    if (a < 0.5) return null;
    return '#' + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  };
  const family = (s) => s.fontFamily.split(',')[0].replace(/["']/g, '').trim();
  const visible = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  const first = (sel) => [...document.querySelectorAll(sel)].find(visible);
  const style = (el) => {
    if (!el) return null;
    const s = getComputedStyle(el);
    return { text: hex(s.color), background: hex(s.backgroundColor), font: family(s), size: s.fontSize,
             weight: s.fontWeight, case: s.textTransform, letterSpacing: s.letterSpacing, radius: s.borderRadius };
  };
  const bg = {}, text = {}, fonts = {};
  for (const el of document.querySelectorAll('body, body *')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    const b = hex(s.backgroundColor);
    if (b) bg[b] = (bg[b] || 0) + r.width * r.height;
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join('');
    const t = hex(s.color);
    if (own && t) {
      text[t] = (text[t] || 0) + own.length;
      if (family(s)) fonts[family(s)] = (fonts[family(s)] || 0) + own.length;
    }
  }
  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([k]) => k);
  const theme = window.Shopify && window.Shopify.theme;
  return JSON.stringify({
    url: location.href,
    shopifyTheme: theme ? { name: theme.name, base: theme.schema_name || null, themeStoreId: theme.theme_store_id || null } : null,
    backgrounds: top(bg, 6),
    textColors: top(text, 6),
    fonts: top(fonts, 4),
    heading: style(first('h1') || first('h2')),
    body: style(first('main p') || first('p')),
    button: style(first('main button, main .button, main [class*="btn"], main a[href*="/collections"]')),
    link: style(first('main p a') || first('main a')),
    header: style(first('header')),
  });
})()
