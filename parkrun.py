import os
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from pathlib import Path
import argparse
import random

# Configuration
EVENT_NAME = "eastville"  # Can be changed via environment variable
BASE_URL = f"https://www.parkrun.org.uk/{EVENT_NAME}/results/weeklyresults/?runSeqNumber={{}}"

# Directory structure
DATA_DIR = Path("data")
HTML_DIR = DATA_DIR / "html" / EVENT_NAME
JSON_DIR = DATA_DIR / "json" / EVENT_NAME

# Create directories if they don't exist
HTML_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

# List of common browser user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15"
]

def get_random_headers(event_name):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": f"https://www.parkrun.org.uk/{event_name}/results/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

def fetch_weekly_result(week_number, json_dir, html_dir, event_name):
    global session
    filename_json = json_dir / f"{week_number}.json"
    filename_html = html_dir / f"{week_number}.html"

    if filename_json.exists():
        with open(filename_json) as f:
            return json.load(f)

    if filename_html.exists():
        with open(filename_html, encoding="utf-8") as f:
            html = f.read()
    else:
        url = f"https://www.parkrun.org.uk/{event_name}/results/{week_number}/"
        time.sleep(2)
        resp = session.get(url, headers=get_random_headers(event_name))
        if resp.status_code != 200:
            print(f"\nWeek {week_number}: HTTP {resp.status_code} - {resp.url}")
            if resp.status_code == 404:
                print("No more results available (404 Not Found)")
                return None
            elif resp.status_code == 425:
                print("No more results available (425 Too Early)")
                return None
            else:
                print(f"Error: {resp.status_code} - trying again in 300 seconds")
                # Reset the session
                session = requests.Session()
                retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
                adapter = HTTPAdapter(max_retries=retries)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                time.sleep(300)  # Take a longer break
                return None
        html = resp.text
        with open(filename_html, "w", encoding="utf-8") as f:
            f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="Results-table")
    if not table:
        print(f"\nWeek {week_number}: No results table found in HTML")
        return None

    results = []
    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        try:
            position = int(row.get("data-position", "0"))
            name = row.get("data-name", "").strip()
            gender = row.get("data-gender", "").strip()
            time_str = get_value_from_row(row, "time")
            age_group = row.get("data-agegroup", "").strip()
            club = row.get("data-club", "").strip()
            runs = row.get("data-runs", "").strip()
            vols = row.get("data-vols", "").strip()
            age_grade = row.get("data-agegrade", "").strip()
            achievement = row.get("data-achievement", "").strip()

            raw_data = {
                "position": position,
                "name": name,
                "gender": gender,
                "time": time_str,
                "age_group": age_group,
                "club": club,
                "runs": runs,
                "vols": vols,
                "age_grade": age_grade,
                "achievement": achievement
            }
            clean_data = {k: v for k, v in raw_data.items() if v}
            results.append(clean_data)

        except Exception:
            continue

    # Save compact JSON without whitespace
    with open(filename_json, "w") as f:
        json.dump({"week": week_number, "results": results}, f, separators=(',', ':'))

    return {"week": week_number, "results": results}

def get_value_from_row(row, class_name):
    tag = row.find("td", class_=f"Results-table-td--{class_name}")
    if tag.find("div", class_="compact"):
        return tag.find("div", class_="compact").get_text(strip=True)
    if tag:
        return tag.get_text(strip=True)
    return ""

def fetch_all_results(event_name):
    print(f"\nFetching {event_name} parkrun results...")
    data_dir = Path("data")
    html_dir = data_dir / "html" / event_name
    json_dir = data_dir / "json" / event_name
    html_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    week = 1
    fetched = 0
    consecutive_failures = 0
    max_consecutive_failures = 3

    while True:
        print(f"\rFetched: {fetched} weeks (current: week {week})", end="", flush=True)
        week_data = fetch_weekly_result(week, json_dir, html_dir, event_name)

        if week_data:
            all_results.append(week_data)
            fetched += 1
            week += 1
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_consecutive_failures:
                print(f"\nStopping after {max_consecutive_failures} consecutive failures")
                break
            week += 1

    print(f"\nCompleted! {fetched} weeks of results saved to {json_dir}")
    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save parkrun results as JSON files.")
    parser.add_argument("event", help="The parkrun event name (e.g. eastville, bushy, etc.)")
    args = parser.parse_args()

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    fetch_all_results(args.event)