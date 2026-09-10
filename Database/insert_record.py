import sys
import json
import sqlite3
from datetime import datetime

LOG_FILE = "pipeline_log.txt"

def log_event(status, record_type, detail):
    """Append one line to the log file: timestamp, status, record type, detail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | {status} | {record_type} | {detail}\n"
    with open(LOG_FILE, "a") as log:
        log.write(line)

# Read the JSON from a file path passed as the first argument
if len(sys.argv) < 2:
    log_event("FAILED", "unknown", "No file provided as argument")
    print("Error: no file provided. Pass a JSON file path as the first argument.")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, "r") as f:
        data = json.load(f)
except FileNotFoundError:
    log_event("FAILED", "unknown", f"File '{file_path}' not found")
    print(f"Error: file '{file_path}' not found.")
    sys.exit(1)
except json.JSONDecodeError as e:
    log_event("FAILED", "unknown", f"Could not parse JSON: {e}")
    print(f"Error: could not parse JSON in file. {e}")
    sys.exit(1)

conn = sqlite3.connect("voygr.db")
cursor = conn.cursor()

record_type = data.get("record_type", "unknown")

try:
    if record_type == "account":
        cursor.execute("""
            INSERT INTO accounts (company_name, vertical, source, enriched_data, date_added)
            VALUES (?, ?, ?, ?, ?);
        """, (
            data.get("company_name"),
            data.get("vertical"),
            data.get("source"),
            data.get("enriched_data"),
            data.get("date_added")
        ))
        conn.commit()
        log_event("SUCCESS", "account", f"account_id {cursor.lastrowid}")
        print(f"Success: account inserted with account_id {cursor.lastrowid}")

    elif record_type == "interaction":
        cursor.execute("""
            INSERT INTO interactions (account_id, type, date, notes, sentiment_tag, human_confirmed, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            data.get("account_id"),
            data.get("type"),
            data.get("date"),
            data.get("notes"),
            data.get("sentiment_tag"),
            data.get("human_confirmed"),
            data.get("outcome")
        ))
        conn.commit()
        log_event("SUCCESS", "interaction", f"interaction_id {cursor.lastrowid}")
        print(f"Success: interaction inserted with interaction_id {cursor.lastrowid}")

    else:
        log_event("FAILED", record_type, f"Unknown record_type '{record_type}'")
        print(f"Error: unknown record_type '{record_type}'. Must be 'account' or 'interaction'.")
        sys.exit(1)

except sqlite3.Error as e:
    log_event("FAILED", record_type, f"Database error: {e}")
    print(f"Database error: {e}")
    sys.exit(1)

finally:
    conn.close()