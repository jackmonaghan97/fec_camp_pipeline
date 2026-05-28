#%%

import requests, json, time

API_KEY = "cXv79V2RQ2HF3M7IMaETTfzcKoKh6SNbPXZpVWiF"
BASE_URL = "https://api.open.fec.gov/v1"
ENDPOINT = "schedules/schedule_b"
PER_PAGE = 100
TARGET = 5000
OUTFILE = "spending_minimal.json"

# choose only the fields you need (example)
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

FILTERS = {"two_year_transaction_period": 2020}

def fetch_until(target):
    
    params = {"api_key": API_KEY, "per_page": PER_PAGE, "page": 1, "fields": FIELDS}
    params.update(FILTERS)
    results = []
    while len(results) < target:
        r = requests.get(f"{BASE_URL}/{ENDPOINT}", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("results", [])
        if not items:
            break
        results.extend(items)
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


# %%
