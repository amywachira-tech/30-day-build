import anthropic
import json
import sqlite3

client = anthropic.Anthropic()

conn = sqlite3.connect("prospects.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS classifications (
    name TEXT,
    company TEXT,
    fit_score INTEGER,
    reasoning TEXT
)
""")

cursor.execute("SELECT name, company FROM prospects")
prospects = cursor.fetchall()

for name, company in prospects:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""Classify this prospect's fit for an AI-powered analytics tool.
Return ONLY valid JSON: {{"fit_score": <1-5>, "reasoning": "<one sentence>"}}

Prospect: {name}, {company}"""
        }]
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        print(f"Skipped {name}: model didn't return valid JSON")
    cursor.execute("SELECT * FROM classifications WHERE fit_score >= 7")
    for row in cursor.fetchall():
        print(row)
conn.commit()
conn.close()