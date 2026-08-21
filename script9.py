import json

with open("prospects.json", "r") as f:
    prospects = json.load(f)

processed = []
skipped = []
for p in prospects:
    try:
        name = p["name"]
        score = p["score"]

        if not name.strip():
            skipped.append(f"{p.get('company', 'UNKNOWN')} — name is empty")
        elif score >= 5:
            processed.append(p)
        else:
            processed.append(p)

    except KeyError as e:
        skipped.append(f"{p.get('name', 'UNKNOWN')} — missing field: {e}")

    except TypeError:
        skipped.append(f"{p['name']} — score is not a valid number (got: {p['score']!r})")
print(f"{len(processed)} processed, {len(skipped)} skipped:")
for reason in skipped:
    print(" -", reason)