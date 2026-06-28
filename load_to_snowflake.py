import snowflake.connector
import pandas as pd
from getpass import getpass

# --- Connection ---
print("Connecting to Snowflake...")
password = getpass("Enter your Snowflake password: ")

conn = snowflake.connector.connect(
    account="krqfxzm-sy74726",
    user="kairamkondap",
    password=password
)
cur = conn.cursor()
print("✓ Connected")

# --- Setup ---
cur.execute("CREATE DATABASE IF NOT EXISTS company_brain")
cur.execute("USE DATABASE company_brain")
cur.execute("CREATE SCHEMA IF NOT EXISTS analytics")
cur.execute("USE SCHEMA analytics")
print("✓ Database and schema ready")

# --- Create Tables ---
cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id     VARCHAR,
    company_name    VARCHAR,
    industry        VARCHAR,
    plan            VARCHAR,
    status          VARCHAR,
    signup_date     DATE,
    mrr             NUMBER,
    country         VARCHAR,
    account_manager VARCHAR
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id         VARCHAR,
    customer_id       VARCHAR,
    category          VARCHAR,
    priority          VARCHAR,
    status            VARCHAR,
    created_date      DATE,
    resolved_date     DATE,
    resolution_days   NUMBER,
    satisfaction_score NUMBER,
    subject           VARCHAR
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id      VARCHAR,
    customer_id     VARCHAR,
    meeting_type    VARCHAR,
    date            DATE,
    duration_mins   NUMBER,
    outcome         VARCHAR,
    attendees       NUMBER,
    action_items    NUMBER,
    notes_summary   VARCHAR
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id              VARCHAR,
    customer_id           VARCHAR,
    event_type            VARCHAR,
    event_date            DATE,
    session_duration_secs NUMBER,
    platform              VARCHAR
)
""")
print("✓ Tables created")

# --- Load Data ---
def load_csv(table, filepath):
    df = pd.read_csv(filepath)
    rows = [tuple(None if pd.isna(v) else v for v in row) 
        for row in df.itertuples(index=False, name=None)]
    placeholders = ", ".join(["%s"] * len(df.columns))
    cur.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    print(f"✓ Loaded {len(rows)} rows into {table}")

for t in ["customers", "tickets", "meetings", "events"]:
    cur.execute(f"TRUNCATE TABLE {t}")

load_csv("customers", "data/customers.csv")
load_csv("tickets",   "data/tickets.csv")
load_csv("meetings",  "data/meetings.csv")
load_csv("events",    "data/events.csv")

conn.commit()
cur.close()
conn.close()
print("\nAll done! Your data is in Snowflake.")