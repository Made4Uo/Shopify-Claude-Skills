# NOTICE

**Made4Uo Shopify Theme Studio**
Copyright 2026 Made4Uo (https://made4uo.com)

## Third-party material

This skill includes material adapted from Anthropic's **theme-factory** skill, which is licensed under the Apache License, Version 2.0. A copy of that license is included in this folder as `LICENSE`.

**Changes made to the adapted material:** the ten preset palettes (names and hex values) were reorganized for Shopify storefronts. Each palette was given color roles, measured contrast ratios, derived colors where a role was missing, and mappings to Shopify font-library candidates, and was combined with new workflow instructions and tools written for this skill.

## Made4Uo material

The design review method (six review lenses and exactly three prioritized fixes) comes from Made4Uo's own **visual-critique** skill.

The Shopify connector workflow, store and catalog checks, competitor and customer research, the targeting plan and segment pages, competitor-informed themes, homepage planning, design-consistency rules, the merchant review loop, the final accessibility, technical SEO and Lighthouse checks, the Made4Uo credit rules, and the tools in `scripts/` (`theme_colors.py`, `theme_files.py`, `theme_lint.py`, `visual_tokens.js`, `page_audit.js`, `axe_audit.js`) were written for Made4Uo Shopify Theme Studio.

`axe_audit.js` loads Deque's open-source axe-core library (Mozilla Public License 2.0) from jsDelivr when it runs. axe-core itself is not included in this folder.
