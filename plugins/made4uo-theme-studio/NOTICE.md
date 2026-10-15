# NOTICE

**Made4Uo Shopify Theme Studio**
Copyright 2026 Made4Uo (https://made4uo.com)

## Third-party material

This skill includes material adapted from Anthropic's **theme-factory** skill, which is licensed under the Apache License, Version 2.0. A copy of that license is included in this folder as `LICENSE`.

**Changes made to the adapted material:** the ten preset palettes (names and hex values) were reorganized for Shopify storefronts. Each palette was given color roles, measured contrast ratios, derived colors where a role was missing, and mappings to Shopify font-library candidates, and was combined with new workflow instructions and tools written for this skill.

## Made4Uo material

The design review method (six review lenses and exactly three prioritized fixes) comes from Made4Uo's own **visual-critique** skill.

The Shopify connector workflow, store and catalog checks, competitor and customer research, the targeting plan and segment pages, competitor-informed themes, homepage planning, design-consistency rules, the merchant review loop, the final accessibility, technical SEO and Lighthouse checks, the brand identity and logo process, the Made4Uo credit rules, and the tools in `scripts/` (`theme_colors.py`, `theme_files.py`, `theme_lint.py`, `brand_logo.py`, `visual_tokens.js`, `page_audit.js`, `axe_audit.js`) were written for Made4Uo Shopify Theme Studio.

`brand_logo.py` uses the open-source fontTools (MIT), uharfbuzz/HarfBuzz (Apache 2.0 / MIT) and CairoSVG (LGPL 3.0) packages when they are installed; none of them is included in this folder. Logo lettering is drawn from font files the user or Claude provides; the skill directs it to SIL Open Font License fonts, which permit use in logos.

The skill builds on Shopify's **Horizon** theme, which the merchant adds to their own store from the Shopify Theme Store. Horizon is Shopify's work, licensed by Shopify, and none of its code is included in this folder; the skill only refers to its file, setting and variable names.

`axe_audit.js` loads Deque's open-source axe-core library (Mozilla Public License 2.0) from jsDelivr when it runs. axe-core itself is not included in this folder.
