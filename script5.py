import json

prospects = [
    {"name": "Jordan Kim", "company": "Nova Energy", "score": 8},
    {"name": "Alex Reyes", "company": "Delta Freight", "score": 4},
    {"name": "Sam Osei", "company": "Solaris Energy", "score": 9},
    {"name": "Priya Nair", "company": "Northwind Trading", "score": 3},
    {"name": "Chen Wei", "company": "Vertex Energy", "score": 7}
]

with open("prospects.json", "w") as f:
    json.dump(prospects, f, indent=2)

print("Written.")