"""Browser check for zezoworkplace.github.io.

Opens each page in a headless browser and fails if:
  - a page does not load, or shows a JavaScript error
  - a link is broken
  - the page scrolls sideways on a phone-sized screen
  - text that Google's OAuth review relies on is missing
    (home page links to the privacy policy, drive.file scope is named)

Usage:
  python tests/site_check.py                          # checks the live site
  python tests/site_check.py http://localhost:8000    # checks a local copy

Screenshots are saved to site-check-screenshots/.

Approach based on the webapp-testing skill from anthropics/skills
(https://github.com/anthropics/skills, Apache-2.0, (c) Anthropic, PBC).
"""

import os
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

LIVE = "https://zezoworkplace.github.io"
BASE = (sys.argv[1] if len(sys.argv) > 1 else LIVE).rstrip("/")
PAGES = ["/", "/privacy.html"]
# Files search engines read; each must load.
SEO_FILES = ["/robots.txt", "/sitemap.xml"]

# Text each page must contain (lower case).
MUST_CONTAIN = {
    "/": ["aureus secure backup", "drive.file"],
    "/privacy.html": ["privacy policy", "auth/drive.file", "retention and deletion"],
}
# Links each page must have.
MUST_LINK_TO = {
    "/": [LIVE + "/privacy.html"],
    "/privacy.html": [LIVE + "/"],
}

PHONE = {"width": 375, "height": 740}
DESKTOP = {"width": 1280, "height": 900}
SHOTS = "site-check-screenshots"

problems = []


def local(url):
    """Point links to the live site at the copy being checked."""
    if url.startswith(LIVE):
        return BASE + url[len(LIVE):]
    return url


def link_works(url):
    req = urllib.request.Request(url, headers={"User-Agent": "site-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status < 400, resp.status
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception as e:  # network error, timeout
        return False, type(e).__name__


def main():
    os.makedirs(SHOTS, exist_ok=True)
    checked_links = {}
    launch = {}
    if os.environ.get("CHROMIUM_PATH"):
        launch["executable_path"] = os.environ["CHROMIUM_PATH"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, **launch)
        for path in PAGES:
            url = BASE + path
            name = path.strip("/").replace(".html", "") or "home"
            for label, size in (("desktop", DESKTOP), ("phone", PHONE)):
                page = browser.new_page(viewport=size)
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on(
                    "console",
                    lambda m: m.type == "error"
                    and not m.text.startswith("Failed to load resource")
                    and errors.append(m.text),
                )
                # Files the page asked for but could not get (the browser's own
                # favicon request is ignored: these pages don't use one).
                page.on(
                    "response",
                    lambda r: r.status >= 400
                    and not r.url.endswith("/favicon.ico")
                    and errors.append(f"could not load {r.url} ({r.status})"),
                )

                resp = page.goto(url, wait_until="networkidle")
                if resp is None or resp.status >= 400:
                    problems.append(f"{path}: page did not load ({resp.status if resp else 'no response'})")
                    page.close()
                    continue
                page.screenshot(path=f"{SHOTS}/{name}-{label}.png", full_page=True)

                for e in errors:
                    problems.append(f"{path} ({label}): browser error: {e}")

                if label == "phone":
                    overflow = page.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                    )
                    if overflow > 1:
                        problems.append(f"{path}: scrolls sideways on a phone by {overflow}px")
                    page.close()
                    continue

                if not page.title().strip():
                    problems.append(f"{path}: page has no title")

                text = page.inner_text("body").lower()
                for phrase in MUST_CONTAIN.get(path, []):
                    if phrase not in text:
                        problems.append(f"{path}: missing text '{phrase}'")

                hrefs = page.eval_on_selector_all("a[href]", "els => els.map(a => a.href)")
                for need in MUST_LINK_TO.get(path, []):
                    if need not in hrefs and local(need) not in hrefs:
                        problems.append(f"{path}: missing link to {need}")

                for href in hrefs:
                    if not href.startswith("http"):
                        continue
                    target = local(href.split("#")[0])
                    if target not in checked_links:
                        checked_links[target] = link_works(target)
                    ok, status = checked_links[target]
                    if not ok:
                        problems.append(f"{path}: broken link {href} ({status})")
                page.close()
        browser.close()

    for path in SEO_FILES:
        ok, status = link_works(BASE + path)
        if not ok:
            problems.append(f"{path}: file did not load ({status})")

    print(f"Checked {len(PAGES)} pages and {len(checked_links)} links on {BASE}")
    if problems:
        print("\nProblems found:")
        for item in problems:
            print("  - " + item)
        sys.exit(1)
    print("All good.")


if __name__ == "__main__":
    main()
