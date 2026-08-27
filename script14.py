import sqlite3

conn = sqlite3.connect("prospects.db")
cursor = conn.cursor()

cursor.execute("""
SELECT companies.industry, COUNT(*) as prospect_count
FROM prospects
JOIN companies ON prospects.company = companies.company
GROUP BY companies.industry
""")

print("Prospects by industry:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")