import os
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine, text

# --- MYSQL CONFIGURATION ---
DB_USER = "omkarpawarfull"
DB_PASSWORD = "Thehouseismine1@"
DB_HOST = "omkarpawarfull.mysql.pythonanywhere-services.com"
DB_NAME = "omkarpawarfull$default"

# Safely encode special characters like '@' in the password
ENCODED_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD)

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}/{DB_NAME}"

CSV_FILE = "netflix_user_events.csv"

def ingest_raw_events():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"File '{CSV_FILE}' not found. Ensure Phase 1 generated it.")

    print(f"Reading CSV dataset: {CSV_FILE}...")
    df = pd.read_csv(CSV_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    print("Connecting to MySQL database...")
    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        print("Recreating table 'raw_user_events'...")
        conn.execute(text("DROP TABLE IF EXISTS raw_user_events;"))
        conn.execute(text("""
            CREATE TABLE raw_user_events (
                event_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                session_id VARCHAR(50),
                timestamp DATETIME,
                event_type VARCHAR(50),
                surface VARCHAR(50),
                platform VARCHAR(50),
                duration_seconds INT
            );
        """))

    print("Ingesting records into MySQL...")
    df.to_sql("raw_user_events", con=engine, if_exists="append", index=False)

    print("Ingestion complete!")

    # Verify record count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM raw_user_events;"))
        count = result.scalar()
        print(f"Total verified records in 'raw_user_events': {count}")

if __name__ == "__main__":
    ingest_raw_events()