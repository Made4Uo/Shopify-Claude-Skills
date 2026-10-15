# Shopify Claude Skills by Made4Uo

Claude plugins and skills that help Shopify merchants design, build and improve their stores with Claude. Created by [Made4Uo](https://made4uo.com).

## Plugins

| Plugin | What it does |
|---|---|
| [**Made4Uo Theme Studio for Shopify**](plugins/made4uo-theme-studio) | Researches your competitors' home and product pages and your customers, designs your brand with an original logo, then builds your store on Shopify's latest Horizon theme: homepage, product page, customer-specific landing pages, trust pages (why shop with us, about, refunds and returns), navigation and footer. It checks in with you at every step and finishes with accessibility, technical SEO and Lighthouse checks. |

More Shopify plugins, such as marketing, are on the way. Once you've added this repository in Claude, new plugins appear in the same list.

## Install

### Claude on the web or desktop

1. Turn on **Settings > Capabilities > Code execution and file creation**.
2. Go to **Customize > Plugins > Add > Add marketplace**.
3. Paste this repository's address: `https://github.com/Made4Uo/shopify-claude-skills`
4. Install **Made4Uo Theme Studio for Shopify** from the list.

### Claude Code

```
/plugin install made4uo-theme-studio --marketplace Made4Uo/shopify-claude-skills
```

## Before you start

- **Connect Shopify's connector for Claude** in the conversation where you use the plugin. All store work goes through it, and Shopify asks you to approve every change.
- **Shopify's free Horizon theme** in your theme library. Claude checks that it's the latest version and asks you to add it from the Theme Store if it isn't there.
- **Optional:** give Claude a browser it can use (Claude in Chrome, or the Claude desktop app's built-in browser). It's needed for reading competitors' styles, preview screenshots and the accessibility checks; without one, Claude skips those and tells you.

## Try it

Ask in plain words, for example:

- "Build a homepage for my candle store."
- "Restyle my store with colors that stand out from my competitors."
- "Design a logo and brand for my new candle shop."
- "Review my homepage and fix the top three issues."
- "Figure out who my customers are and create pages for them."

## How it keeps your store safe

- Claude edits only an **unpublished** theme and keeps backups of every file it changes. You preview the result and publish it yourself when you're happy.
- Claude never publishes a theme, deletes a theme, or changes prices or inventory, and never edits the menus your live store uses.
- You check every piece of work (the research, the brand board, page drafts, built pages, the preview) and say the word to change anything. Pages, menus and policies are created only after you approve them.
- Reviews, ratings, guarantees and other trust signals come only from your store's real data or from you. Nothing is invented.
- **Made4Uo receives no data.** The plugin README lists [everything the plugin runs, sends and fetches](plugins/made4uo-theme-studio/README.md#what-it-runs-sends-and-fetches).

## Repository layout

```
.claude-plugin/marketplace.json        the list of plugins Claude reads from this repository
plugins/made4uo-theme-studio/          the Theme Studio plugin
  .claude-plugin/plugin.json           plugin name, version and description
  skills/shopify-theme-studio/         the skill (SKILL.md) and its tools (scripts/)
  README.md, LICENSE, NOTICE.md        plugin details, license and credits
```

## Adding a plugin

1. Create `plugins/<plugin-name>/` with `.claude-plugin/plugin.json`, a `README.md`, a `LICENSE`, and each skill in `skills/<skill-name>/SKILL.md`. Use lowercase letters, digits and hyphens for names, and start each plugin name with `made4uo-`.
2. Add an entry for it to the `plugins` list in `.claude-plugin/marketplace.json`.
3. Check everything with Claude Code from the repository root: `claude plugin validate .` and `claude plugin validate ./plugins/<plugin-name>`.
4. Raise `version` in `plugin.json` and in `marketplace.json` with every release.
5. To list it in Claude's public directory, submit the plugin folder on its own in the developer portal at [claude.ai/directory/manage](https://claude.ai/directory/manage), entering `plugins/<plugin-name>` as the plugin path.

## License

Apache License 2.0. Each plugin folder carries its own `LICENSE` and `NOTICE.md`. Theme Studio includes material adapted from Anthropic's theme-factory skill.

## About Made4Uo

Learn more about Shopify customization at [made4uo.com](https://made4uo.com).
