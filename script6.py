import json

with open("prospects.json", "r") as f:
    prospects = json.load(f)

high_score = [p for p in prospects if p["score"] >= "7"

with open("high_score_prospects.json", "w") as f:
    json.dump(high_score, f, indent=2)

print(f"{len(high_score)} prospects met the threshold.")