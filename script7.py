import json

import json

prospects = [
    {"name": "Jordan Kim", "company": "Nova Energy",
     "contact": {"email": "jordan.kim@novaenergy.com", "phone": "555-0101"}},
    {"name": "Sam Osei", "company": "Solaris Energy",
     "contact": {"email": "sam.osei@solarisenergy.com", "phone": "555-0102"}}
]

with open("nested_prospects.json", "w") as f:
    json.dump(prospects, f, indent=2)

with open("nested_prospects.json", "r") as f:
    loaded = json.load(f)

for p in loaded:
    print(p["name"], "-", p["contact"]["email"])