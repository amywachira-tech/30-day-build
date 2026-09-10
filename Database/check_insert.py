import sqlite3

conn = sqlite3.connect("voygr.db")
cursor = conn.cursor()

# Insert one fake account
cursor.execute("""
INSERT INTO accounts (company_name, vertical, source, enriched_data, date_added)
VALUES (?, ?, ?, ?, ?);
""", (
    "Acme Freight Co",
    "logistics",
    "purchased contact list",
    "employee count: 45, LinkedIn: linkedin.com/company/acme-freight",
    "2026-09-09"
))

# Get the account_id that was just created, so we can link the interaction to it
new_account_id = cursor.lastrowid

# Insert one fake interaction linked to that account
cursor.execute("""
INSERT INTO interactions (account_id, type, date, notes, sentiment_tag, human_confirmed, outcome)
VALUES (?, ?, ?, ?, ?, ?, ?);
""", (
    new_account_id,
    "email_reply",
    "2026-09-09",
    "Asked for pricing details on multi-site connectivity.",
    "positive",
    "yes",
    "open"
))

conn.commit()

# Now query both tables joined together, to prove the link works
cursor.execute("""
SELECT accounts.company_name, accounts.vertical, interactions.type, interactions.sentiment_tag
FROM accounts
JOIN interactions ON accounts.account_id = interactions.account_id;
""")

print("Joined result:", cursor.fetchall())

conn.close()