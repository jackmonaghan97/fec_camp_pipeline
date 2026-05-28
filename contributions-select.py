import requests, json, time

API_KEY = "wacTY0J0dINpMTUOVGRSTJRFgOVXpxkIhbZ7erDH"  # replace with your key
BASE_URL = "https://api.open.fec.gov/v1"
ENDPOINT = "schedules/schedule_a"
PER_PAGE = 100
TARGET = 1000
OUTFILE = "contribs.json"
# pick a single two_year_transaction_period (e.g., 2020 or 2022)
TWO_YEAR = 2020

def fetch_until(target):
    params = {
        "api_key": API_KEY,
        "per_page": PER_PAGE,
        "page": 1,
        "two_year_transaction_period": TWO_YEAR
    }
    results = []
    while len(results) < target:
        resp = requests.get(f"{BASE_URL}/{ENDPOINT}", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        page_items = data.get("results", [])
        if not page_items:
            break
        results.extend(page_items)
        pagination = data.get("pagination", {})
        if params["page"] >= pagination.get("pages", 0):
            break
        params["page"] += 1
        time.sleep(0.2)
    return results[:target]

if __name__ == "__main__":
    rows = fetch_until(TARGET)
    print(f"Fetched {len(rows)} rows")
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Saved to {OUTFILE}")

