import requests, json

API_KEY = "wacTY0J0dINpMTUOVGRSTJRFgOVXpxkIhbZ7erDH"
BASE_URL = "https://api.open.fec.gov/v1"
ENDPOINT = "candidates/search"
PARAMS = {"q": "Biden", "api_key": API_KEY}

def fetch_all(endpoint, params):
    
    all_results = []
    page = 1
    while True:
        params["page"] = page
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        all_results.extend(results)

        # Use pagination info to know when to stop
        pagination = data.get("pagination", {})
        total_pages = pagination.get("pages")
        if not total_pages or page >= total_pages:
            break
        page += 1
    return all_results

if __name__ == "__main__":
    rows = fetch_all(ENDPOINT, PARAMS)
    print(f"Fetched {len(rows)} rows")
    print(json.dumps(rows, indent=2))
