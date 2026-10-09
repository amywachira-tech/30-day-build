import json

with open("prospects.json", "r") as f:
    prospects = json.load(f)

high_score = [
    p for p in prospects
    if isinstance(p.get("score"), (int, float)) and p["score"] >= 7
]

with open("high_score_prospects.json", "w") as f:
    json.dump(high_score, f, indent=2)

print(f"{len(high_score)} prospects met the threshold.")