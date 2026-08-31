import os
import math
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Missing SUPABASE_URL or SUPABASE_KEY in .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

df = pd.read_csv("data/diamonds.csv")
records = df.to_dict(orient="records")

BATCH_SIZE = 500
total_batches = math.ceil(len(records) / BATCH_SIZE)
print(f"Uploading {len(records)} rows in {total_batches} batches...")

for i in range(0, len(records), BATCH_SIZE):
    batch = records[i : i + BATCH_SIZE]
    supabase.table("diamonds").insert(batch).execute()
    print(f"  uploaded batch {i // BATCH_SIZE + 1}/{total_batches}")

print("Done.")