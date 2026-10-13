# Made4Uo Theme Studio for Shopify

Design, build and check a Shopify store theme with Claude. Made4Uo Theme Studio turns Claude into a careful storefront designer: it researches your competitors and customers, suggests color and font themes based on that research, builds a consistent homepage and customer-specific landing pages in an unpublished copy of your theme, reviews the result with you, and finishes with accessibility, technical SEO and Lighthouse checks.

Created by [Made4Uo](https://made4uo.com).

## What it does

- **Checks your store first.** Claude compares your products with what you ask for and stops to ask if they don't match.
- **Researches the market.** It studies at least three competitors (offer, trust signals, colors and fonts) and, if you haven't said who your customers are, proposes customer segments with the evidence behind them.
- **Suggests themes from the research,** alongside ten preset palettes, with every color pair checked for readability.
- **Builds with one design system.** New work reuses your theme's sections, blocks and CSS variables, and a built-in checker flags hard-coded colors, fonts and sizes.
- **Works safely.** Claude edits only an unpublished theme, keeps backups of every file it changes, and never publishes, deletes themes, or changes prices or inventory.
- **Reviews with you, then finalizes.** You see the preview and ask for changes; only after you approve does Claude run accessibility (axe-core), technical SEO and Lighthouse checks and report the scores.

## Requirements

- **Shopify's connector for Claude,** connected in your conversation. Theme Studio does all store work through it, and Shopify asks you to approve every change.
- **Code execution** turned on in Claude, for the bundled Python tools.
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
- "Review my homepage and fix the top three issues."
- "Figure out who my customers are and create pages for them."

## What it runs, sends and fetches

- **Your Shopify store,** through Shopify's connector: reads shop details, products, collections, inventory, themes and theme files, and sales analytics (totals only, never individual customers' details). With your approval it writes theme files to an unpublished theme, and can create pages, collections, menus and images in Files.
- **Public web pages** of competitors and search results, read for research.
- **In the browser:** `visual_tokens.js` and `page_audit.js` read colors, fonts and SEO and accessibility signals from the page being checked. `axe_audit.js` loads the open-source axe-core library from cdn.jsdelivr.net into the page it audits.
- **Google PageSpeed Insights** receives your store's page address when Claude runs Lighthouse, and only if the page is public.
- **Local tools** (`theme_colors.py`, `theme_files.py`, `theme_lint.py`) run inside Claude's workspace and make no network requests.
- **Made4Uo receives no data.** New theme files carry a short hidden code comment crediting Made4Uo, which shoppers never see, and a visible footer credit is added only if you say yes.

## License

Apache License 2.0. See `LICENSE` and `NOTICE.md`. Includes material adapted from Anthropic's theme-factory skill.
