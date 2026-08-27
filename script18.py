import anthropic
import json
import sqlite3

client = anthropic.Anthropic()

conn = sqlite3.connect("prospects.db")
cursor = conn.cursor()
cursor.execute("SELECT name, company FROM prospects")
prospects = cursor.fetchall()
conn.close()

results = []

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
raw = response.content[0].text
raw = raw.strip()
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
raw = raw.strip()

parsed = json.loads(raw)
results.append({"name": name, "company": company, **parsed})
print(f"{name} ({company}): {parsed['fit_score']} — {parsed['reasoning']}")