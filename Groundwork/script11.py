import sqlite3
import json

conn = sqlite3.connect("prospects.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prospects (
    name TEXT,
    company TEXT,
    score INTEGER
)
""")

with open("prospects.json", "r") as f:
    prospects = json.load(f)

for p in prospects:
    if "score" in p and isinstance(p["score"], (int, float)) and p.get("name"):
        cursor.execute(
            "INSERT INTO prospects (name, company, score) VALUES (?, ?, ?)",
            (p["name"], p["company"], p["score"])
        )

conn.commit()
print("Database built.")
cursor.execute("SELECT * FROM prospects WHERE score >= 7")
for row in cursor.fetchall():
    print(row)