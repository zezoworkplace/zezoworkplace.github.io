# zezoworkplace.github.io
AUREUS Secure Backup — OAuth information pages

## Site check

`.github/workflows/site-check.yml` opens each page in a headless browser and fails if a page
has an error, a broken link, sideways scrolling on a phone, or is missing the text Google's
OAuth review relies on. It runs on every change and every Monday against the live site.
You can also start it from the Actions tab ("Site check" → "Run workflow").

Run it yourself: `pip install playwright && python -m playwright install chromium && python tests/site_check.py`

Based on the webapp-testing skill from [anthropics/skills](https://github.com/anthropics/skills) (Apache-2.0, © Anthropic, PBC).
