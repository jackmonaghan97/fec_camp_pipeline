#%%

import json
import pandas as pd
import duckdb
from datetime import datetime

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

df = pd.read_json('spending_minimal.json')[FIELDS.split(',')]

# Coerce types: dates and numeric
if "disbursement_date" in df.columns:
    df["disbursement_date"] = pd.to_datetime(df["disbursement_date"], errors="coerce")
if "disbursement_amount" in df.columns:
    df["disbursement_amount"] = pd.to_numeric(df["disbursement_amount"], errors="coerce")

# Write to DuckDB (append if table exists)
con = duckdb.connect(DB_PATH)
# register pandas DF as a view then create/insert
con.register("tmp_df", df)
# create table if doesn't exist (with same columns)
con.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE} AS
SELECT * FROM tmp_df
""")
# If table already existed and you want to append instead:
# con.execute(f"INSERT INTO {TABLE} SELECT * FROM tmp_df")
con.unregister("tmp_df")
con.close()

# %%
