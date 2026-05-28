# %%


#!/usr/bin/env python3
import requests, json, time, duckdb
from pathlib import Path

API_KEY = "cXv79V2RQ2HF3M7IMaETTfzcKoKh6SNbPXZpVWiF"
BASE_URL = "https://api.open.fec.gov/v1"
ENDPOINT = "schedules/schedule_b"
PER_PAGE = 100
TARGET = 100000
STATE_PATH = Path("fetch_state.json")
DB_PATH = r"C:\Users\jackm\OneDrive\Documents\duckdb_cli-windows-amd64\my_database.duckdb"
TABLE = "spending"

FIELDS = ",".join([
    'amendment_indicator', 'amendment_indicator_desc',       
    'beneficiary_committee_name', 'candidate_name',
    'candidate_office_description', 'candidate_office_state',
    'candidate_office_state_full', 'category_code_full', 
    'comm_dt', 'committee', 'disbursement_amount',
    'disbursement_date', 'disbursement_description',
    'disbursement_purpose_category', 'disbursement_type_description',
    'entity_type_desc', 'fec_election_year',
    'payee_first_name', 'payee_last_name',
    'payee_middle_name', 'payee_occupation',
    'recipient_city', 'recipient_name', 'recipient_state',
    'recipient_zip', 'spender_committee_designation',
    'spender_committee_org_type', 'spender_committee_type'
])
COLS = [c.strip() for c in FIELDS.split(",")]
FILTERS = {"two_year_transaction_period": 2020}
BROKEN_ROWS = []

def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"page": 1, "fetched": 0}

def save_state(state):
    STATE_PATH.write_text(json.dumps(state))

def ensure_table():
    
    con = duckdb.connect(DB_PATH)
    cols_defs = ", ".join(f"{c} VARCHAR" for c in COLS)
    con.execute(f"CREATE TABLE IF NOT EXISTS {TABLE} ({cols_defs})")
    con.close()

def insert_rows(rows):
    

    if not rows:
        return
    
    for i in rows: {c: i.get(c) for c in COLS}
    try:
        con = duckdb.connect(DB_PATH)
        cols_order = COLS
        placeholders = ",".join(["?"] * len(cols_order))
        con.executemany(f"INSERT INTO {TABLE} VALUES ({placeholders})",
                        [[r.get(col) for col in cols_order] for r in rows])
        con.close()

    except Exception as e:
        BROKEN_ROWS.extend(rows)
        print(f"Error occurred while inserting rows: {e}")

def flatten_item(item):
    row = {c: None for c in COLS}
    # top-level copy (only if key exists)
    for k in COLS:
        if k in item:
            row[k] = item.get(k)
    # extract nested committee object if present
    committee = item.get("committee") or {}
    row["committee_id"] = committee.get("committee_id")
    row["committee_affiliated_name"] = committee.get("affiliated_committee_name") or committee.get("name")
    return row

def fetch_until(target):
    state = load_state()
    page = state.get("page", 1)
    fetched = state.get("fetched", 0)
    backoff = 1.0

    params = {"api_key": API_KEY, "per_page": PER_PAGE, "page": page, "fields": FIELDS}
    params.update(FILTERS)

    while fetched < target:
        try:
            r = requests.get(f"{BASE_URL}/{ENDPOINT}", params=params, timeout=30)
        except Exception:
            time.sleep(min(backoff, 60))
            backoff = min(backoff * 2, 60)
            continue

        if r.status_code == 429:
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
            continue

        r.raise_for_status()
        data = r.json()
        items = data.get("results", [])
        if not items:
            break

        batch = []
        for it in items:
            batch.append(flatten_item(it))
            fetched += 1
            if fetched >= target:
                break
        for i, r in enumerate(batch):
            for k, v in r.items():
                if v is not None and 'H8TN02242' in str(v):
                    print("broken row", i, k, v)

        insert_rows(batch)

        page += 1
        params["page"] = page
        state = {"page": page, "fetched": fetched}
        save_state(state)

        time.sleep(0.2)
        backoff = 1.0

        pagination = data.get("pagination", {})
        total_pages = pagination.get("pages")
        if total_pages and page > total_pages:
            break

    return fetched

if __name__ == "__main__":
    ensure_table()
    print(f"Starting fetch target={TARGET}")
    total = fetch_until(TARGET)
    print(f"Fetched and stored {total} rows into {DB_PATH}:{TABLE}")

# %%
