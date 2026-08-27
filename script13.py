import sqlite3

conn = sqlite3.connect("prospects.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company TEXT PRIMARY KEY,
    industry TEXT
)
""")

companies_data = [
    ("Nova  Energy", "Energy"),
    ("Solaris Energy", "Energy"),
    ("Delta Freight", "Logistics"),
    ("Northwind Trading", "Trading"),
    ("SupportLogic", "Software"),
    ("Drip", "Marketing"),
    ("Hudl", "Sports Tech"),
    ("Evergreen", "Consulting"),
    ("Titus", "Retail"),
    ("Elena Energy", "Energy")
]

cursor.executemany("INSERT OR IGNORE INTO companies (company, industry) VALUES (?, ?)", companies_data)
conn.commit()

cursor.execute("""
SELECT prospects.name, prospects.score, companies.industry
FROM prospects
JOIN companies ON prospects.company = companies.company
""")

for row in cursor.fetchall():
    print(row)