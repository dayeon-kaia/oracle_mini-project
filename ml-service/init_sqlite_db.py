import sqlite3
import pandas as pd
import os

DB_PATH = "mock_data.db"
CSV_PATH = "mock_icu_data.csv"

def init_db():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found.")
        return

    # Load CSV
    df = pd.read_csv(CSV_PATH)
    
    # Rename columns to be more SQL friendly if needed (already good: stay_id, charttime, etc)
    # Ensure datetime is parsed
    # df['charttime'] = pd.to_datetime(df['charttime']) # SQLite stores as text usually, which is fine
    
    # Connect/Create SQLite DB
    conn = sqlite3.connect(DB_PATH)
    
    # Write to table 'icu_vitals'
    df.to_sql("icu_vitals", conn, if_exists="replace", index=False)
    
    print(f"✅ Successfully created {DB_PATH} with table 'icu_vitals' ({len(df)} rows)")
    
    # Check
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    conn.close()

if __name__ == "__main__":
    init_db()
