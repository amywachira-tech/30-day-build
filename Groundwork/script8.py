import json

prospects = [
    {"name": "Jordan Kim", "company": "Nova Energy", "score":9},
    {"name": "Sam Osei", "company": "Solaris Energy", "score": 6},
    {"name": "Jane Eyre", "company": "SupportLogic", "score": 5},
    {"name": "John Doe", "company": "Drip", "score": 7},
    {"name": "Jamie Dornan", "company": "Hudl", "score": 4},
    {"name": "Claire Fraser", "company": "Evergreen", "score": "eight"},
    {"name": "Kimmy Schmidt", "company": "Titus"},
    {"name": "", "company": "Elena Energy", "score": 9}
]
with open("prospects.json", "w") as f:
    json.dump(prospects, f, indent=2)