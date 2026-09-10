import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect("voygr.db")
cursor = conn.cursor()

# Enable foreign key support (SQLite has this off by default)
cursor.execute("PRAGMA foreign_keys = ON;")

# Create the accounts table
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

# Create the interactions table, linked to accounts via account_id
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

# Save changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully.")