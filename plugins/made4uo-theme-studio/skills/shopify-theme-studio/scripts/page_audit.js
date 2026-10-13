(() => {
  const q = (sel) => [...document.querySelectorAll(sel)];
  const meta = (sel) => { const m = document.querySelector(sel); return m ? (m.getAttribute('content') || '').trim() : null; };
  const txt = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim();
  const visible = (el) => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const accessibleName = (el) => (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.getAttribute('title')
    || txt(el) || (el.querySelector('img[alt]:not([alt=""]), svg[aria-label], [aria-label]') ? 'has-labelled-child' : '')).trim();
  const h1s = q('h1').filter(visible);
  const levels = q('h1, h2, h3, h4, h5, h6').filter(visible).map((h) => Number(h.tagName[1]));
  const imgs = q('img');
  const fold = window.innerHeight || 800;
  const aboveFold = imgs.filter((i) => visible(i) && i.getBoundingClientRect().top < fold);
  const schemaTypes = q('script[type="application/ld+json"]').flatMap((s) => {
    try { const d = JSON.parse(s.textContent); return (Array.isArray(d) ? d : [d]).map((x) => x['@type'] || '?'); }
    catch (e) { return ['INVALID JSON-LD']; }
  });
  const ids = q('[id]').map((e) => e.id).filter(Boolean);
  const fields = q('input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=image]), select, textarea').filter(visible);
  const title = document.title.trim();
  const description = meta('meta[name="description"]');
  const canonical = document.querySelector('link[rel="canonical"]');
  return JSON.stringify({
    url: location.href,
    seo: {
      title, titleLength: title.length,
      description, descriptionLength: description ? description.length : 0,
      canonical: canonical ? canonical.href : null,
      robots: meta('meta[name="robots"]'),
      lang: document.documentElement.getAttribute('lang'),
      viewport: meta('meta[name="viewport"]'),
      h1Count: h1s.length, h1: h1s.slice(0, 3).map(txt),
      headingLevelSkips: levels.filter((l, i) => i > 0 && l > levels[i - 1] + 1).length,
      structuredData: schemaTypes,
      openGraph: { title: meta('meta[property="og:title"]'), image: meta('meta[property="og:image"]'), type: meta('meta[property="og:type"]') },
      twitterCard: meta('meta[name="twitter:card"]'),
      linksWithoutName: q('a[href]').filter(visible).filter((a) => !accessibleName(a)).length,
    },
    accessibility: {
      imagesMissingAlt: imgs.filter((i) => !i.hasAttribute('alt')).length,
      buttonsWithoutName: q('button, [role="button"]').filter(visible).filter((b) => !accessibleName(b)).length,
      unlabeledFields: fields.filter((f) => !(f.labels && f.labels.length) && !f.getAttribute('aria-label')
        && !f.getAttribute('aria-labelledby') && !f.getAttribute('title')).length,
      skipLink: q('a[href^="#"]').some((a) => /skip|content|main/i.test(txt(a) + ' ' + a.getAttribute('href'))),
      positiveTabindex: q('[tabindex]').filter((e) => Number(e.getAttribute('tabindex')) > 0).length,
      duplicateIds: [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))].slice(0, 10),
    },
    performance: {
      images: imgs.length,
      imagesWithoutSize: imgs.filter((i) => !(i.getAttribute('width') && i.getAttribute('height'))).length,
      lazyLoadedAboveFold: aboveFold.filter((i) => i.getAttribute('loading') === 'lazy').length,
      blockingScriptsInHead: q('head script[src]:not([async]):not([defer]):not([type="module"])').length,
      stylesheets: q('link[rel="stylesheet"]').length,
    },
  });
})()
