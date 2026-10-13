(async () => {
  const VERSION = '4.14.0';
  // Subresource Integrity: the browser runs the file only if it matches this hash of axe-core 4.14.0 exactly.
  const INTEGRITY = 'sha384-lFUXB8tI4BaTE1bqxH9eeAXON2NH1qsdAhs7S5L++nUNP5QOy+hwr0C3TYEJUEl0';
  if (!window.axe) {
    await new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = `https://cdn.jsdelivr.net/npm/axe-core@${VERSION}/axe.min.js`;
      s.integrity = INTEGRITY;
      s.crossOrigin = 'anonymous';
      s.onload = resolve;
      s.onerror = () => reject(new Error('could not load axe-core, or it failed its integrity check'));
      document.head.appendChild(s);
    });
  }
  const r = await window.axe.run(document, {
    resultTypes: ['violations'],
    runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
  });
  const rank = { critical: 0, serious: 1, moderate: 2, minor: 3 };
  const issues = (impact) => r.violations.filter((v) => v.impact === impact).reduce((n, v) => n + v.nodes.length, 0);
  const out = JSON.stringify({
    url: location.href,
    axe: window.axe.version,
    rulesFailed: r.violations.length,
    rulesPassed: r.passes.length,
    needsManualReview: r.incomplete.length,
    issues: { critical: issues('critical'), serious: issues('serious'), moderate: issues('moderate'), minor: issues('minor') },
    top: [...r.violations].sort((a, b) => rank[a.impact] - rank[b.impact] || b.nodes.length - a.nodes.length).slice(0, 15)
      .map((v) => ({ rule: v.id, impact: v.impact, count: v.nodes.length, help: v.help,
                     example: v.nodes[0] ? v.nodes[0].target.join(' ') : null })),
  });
  window.__studioAxe = out;
  return out;
})()
