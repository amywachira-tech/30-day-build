import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def init_db():
    """Create the tables if they don't exist yet, same schema as setup_db.py."""
    conn = sqlite3.connect("voygr.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        vertical TEXT,
        source TEXT,
        enriched_data TEXT,
        date_added TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        type TEXT,
        date TEXT,
        notes TEXT,
        sentiment_tag TEXT,
        human_confirmed TEXT,
        outcome TEXT,
        FOREIGN KEY (account_id) REFERENCES accounts (account_id)
    );
    """)

    conn.commit()
    conn.close()

@app.route("/insert", methods=["POST"])
def insert():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON body provided"}), 400

    record_type = data.get("record_type")
    conn = sqlite3.connect("voygr.db")
    cursor = conn.cursor()

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
            new_id = cursor.lastrowid
            return jsonify({"status": "success", "account_id": new_id})

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
            new_id = cursor.lastrowid
            return jsonify({"status": "success", "interaction_id": new_id})

        else:
            return jsonify({"status": "error", "message": f"Unknown record_type '{record_type}'"}), 400

    except sqlite3.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        conn.close()

@app.route("/", methods=["GET"])
def health_check():
    """Simple endpoint to confirm the service is alive."""
    return jsonify({"status": "running"})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)