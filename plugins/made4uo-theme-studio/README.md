# Made4Uo Theme Studio for Shopify

Design, build and check a Shopify store theme with Claude. Made4Uo Theme Studio turns Claude into a careful storefront designer: it researches your competitors and customers, suggests color and font themes based on that research, builds a consistent homepage, product page and customer-specific landing pages on an unpublished copy of Shopify's latest Horizon theme, reviews the result with you, and finishes with accessibility, technical SEO and Lighthouse checks.

Created by [Made4Uo](https://made4uo.com).

## What it does

- **Checks your store first.** Claude compares your products with what you ask for and stops to ask if they don't match.
- **Always starts from the latest Horizon.** Every build uses Shopify's free Horizon theme at its newest released version. If your store doesn't have it yet, Claude asks you to add it from the Theme Store (one click) and checks the version before building.
- **Researches the market.** It audits the homepage and a product page of at least three competitors on mobile and desktop (first screen, section order, offer, buying controls, reassurance near the button, trust signals, colors and fonts) and, if you haven't said who your customers are, proposes customer segments with the evidence behind them.
- **Designs your brand.** Right after the research, Claude designs two or three brand directions, each with an original logo (header logo, stacked logo and a mark for the favicon), colors, fonts, voice and photo direction, and presents them as a brand board with mockups of your store. You pick one, ask for changes, and get the logo files and a short brand guide. Already have a logo? Claude builds around it instead.
- **Suggests colors and fonts from the research,** alongside ten preset palettes, with every color pair checked for readability.
- **Builds the pages that earn trust.** A "Why shop with us" page that explains, without naming rivals, what shoppers usually get in your category and what you do differently; an About page with your story and, for handmade products, how they're made; and a plain-language Refunds & returns page. Missing policies are drafted for your review.
- **Sets up navigation and footer.** New header and footer menus for the new theme only (your live store's menus stay untouched): collections plus "Why shop with us" in the header; About, Refunds & returns, Contact and your policies in the footer; and "All rights reserved." in place of "Powered by Shopify".
- **Keeps product grids even.** One image ratio and card size across every product grid.
- **Checks in with you at every step.** You see the research, the brand board, the page drafts, the built pages and the preview; say the word and Claude changes anything.
- **Builds with one design system.** New work reuses Horizon's sections, theme blocks, color palette and CSS variables, and a built-in checker flags hard-coded colors, fonts and sizes.
- **Works safely.** Claude edits only an unpublished theme, keeps backups of every file it changes, and never publishes, deletes themes, or changes prices or inventory.
- **Reviews with you, then finalizes.** You see the preview and ask for changes; only after you approve does Claude run accessibility (axe-core), technical SEO and Lighthouse checks and report the scores.

## Requirements

- **Shopify's connector for Claude,** connected in your conversation. Theme Studio does all store work through it, and Shopify asks you to approve every change.
- **Shopify's Horizon theme** (free) in your theme library at its latest version. Claude checks for it and asks you to add it if it's missing or out of date.
- **Code execution** turned on in Claude, for the bundled Python tools. The logo tool also uses the `fonttools`, `uharfbuzz`, `cairosvg` and `pillow` Python packages, which Claude installs if they're missing.
- **Optional:** a browser Claude can use (Claude in Chrome or the Claude desktop app's browser) for competitor style reading, preview screenshots and accessibility checks. Without one, Claude skips those checks and tells you.

## Install

- **Claude on the web or desktop:** go to **Customize > Plugins > Add > Add marketplace**, paste `https://github.com/Made4Uo/shopify-claude-skills`, then install Made4Uo Theme Studio for Shopify.
- **Claude Code:** run this command:

```
/plugin install made4uo-theme-studio --marketplace Made4Uo/shopify-claude-skills
```

## How to use it

Connect Shopify's connector, then ask in plain words, for example:

- "Build a homepage for my candle store."
- "Restyle my store with colors that stand out from my competitors."
- "Design a logo and brand for my new candle shop."
- "Review my homepage and fix the top three issues."
- "Figure out who my customers are and create pages for them."

## What it runs, sends and fetches

- **Your Shopify store,** through Shopify's connector: reads shop details, products, collections, inventory, pages, menus, store policies, themes and theme files, and sales analytics (totals only, never individual customers' details). With your approval it writes theme files to an unpublished theme, and can create pages, collections, new menus for the new theme, store policies you've approved, and images (such as your logo) in Files. It never edits the menus your live theme uses.
- **Public web pages** of competitors and search results, read for research, and open-licensed font files from Google Fonts' GitHub repository, downloaded for logo lettering.
- **Logo files** are uploaded to your store's Files through Shopify's upload service, with your approval. If Claude's workspace can't reach it, Claude sends you the files to upload in the theme editor.
- **In the browser:** `visual_tokens.js` and `page_audit.js` read colors, fonts and SEO and accessibility signals from the page being checked. `axe_audit.js` loads the open-source axe-core library (version 4.14.0) from cdn.jsdelivr.net into the page it audits; the browser runs it only if it matches a fixed integrity hash of that exact file.
- **Google PageSpeed Insights** receives your store's page address when Claude runs Lighthouse, and only if the page is public.
- **Local tools** (`theme_colors.py`, `theme_files.py`, `theme_lint.py`, `brand_logo.py`) run inside Claude's workspace and make no network requests.
- **Made4Uo receives no data.** New theme files carry a short hidden code comment crediting Made4Uo, which shoppers never see, and a visible footer credit is added only if you say yes.

## Privacy

Made4Uo Theme Studio is a set of instructions and small tools that run inside your own Claude session. Made4Uo runs no server for it and receives no data from it.

- **What it reads:** your store's details (including the store owner's name and contact email), products, collections, inventory, pages, menus, store policies, themes and theme files, and sales totals, all through Shopify's connector, which you connect and control. It never reads individual customers' names or details.
- **What it stores:** nothing. Copies of theme files that Claude keeps for undo, and draft logo files, exist only in that session's workspace and are design files, not personal data. Anything Claude writes goes into your own Shopify store, with your approval.
- **What it sends elsewhere:** only what is listed above under "What it runs, sends and fetches": page addresses to Google PageSpeed Insights, requests to cdn.jsdelivr.net for the accessibility checker, font downloads from Google Fonts' GitHub repository, your logo files to Shopify's own upload service, and web searches and visits to public competitor pages.
- **Your conversation** with Claude is handled under Anthropic's own policies, separately from this plugin.

Questions about privacy: contact Made4Uo through [made4uo.com](https://made4uo.com).

## License

Apache License 2.0. See `LICENSE` and `NOTICE.md`. Includes material adapted from Anthropic's theme-factory skill.
