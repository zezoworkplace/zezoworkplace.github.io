# zezoworkplace.github.io
AUREUS Secure Backup — OAuth information pages

## Site check

`.github/workflows/site-check.yml` opens each page in a headless browser and fails if a page
has an error, a broken link, sideways scrolling on a phone, or is missing the text Google's
OAuth review relies on. It runs on every change and every Monday against the live site.
You can also start it from the Actions tab ("Site check" → "Run workflow").

Run it yourself: `pip install playwright && python -m playwright install chromium && python tests/site_check.py`

Based on the webapp-testing skill from [anthropics/skills](https://github.com/anthropics/skills) (Apache-2.0, © Anthropic, PBC).

## Search engine basics

`robots.txt` and `sitemap.xml` tell search engines (and Google Search Console) which pages exist.
Each page also has link-preview tags (`og:` and `twitter:`). Checklist taken from the SEO skills in
[kostja94/marketing-skills](https://github.com/kostja94/marketing-skills) (MIT, © 2025 kostja94).
If you add a page, add it to `sitemap.xml` and to `PAGES` in `tests/site_check.py`.
