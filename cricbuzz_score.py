from playwright.sync_api import sync_playwright
import re

URL = "https://www.cricbuzz.com/live-cricket-scores/155422/ausa-vs-inda-2nd-unofficial-test-australia-a-tour-of-india-2026"


def extract_live_score(page_text: str):
    """Return the most likely cricket score from the page text."""
    candidates = re.findall(r"\d+\s*(?:/\s*\d+|-\s*\d+)(?:\s*\(\d+\))?", page_text)
    if not candidates:
        return None

    filtered = []
    for candidate in candidates:
        if re.search(r"\b(?:19|20)\d{2}\b", candidate):
            continue
        if candidate.count("/") > 0 or candidate.count("-") > 0:
            filtered.append(candidate)

    if not filtered:
        filtered = candidates

    # Prefer score-style values with a slash, then the longest candidate.
    score = max(filtered, key=lambda value: ("/" in value, len(value)))
    return re.sub(r"\s+", " ", score).strip()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text()
        score = extract_live_score(body_text)

        if score:
            print(f"Live Score: {score}")
        else:
            print("No score pattern found in page text.")

        page.screenshot(path="score.png", full_page=True)
    except Exception as exc:
        print(f"Error: {exc}")
    finally:
        browser.close()