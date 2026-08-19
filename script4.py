prospects = [
    {"name": "Jordan Kim", "company": "Nova Trading"},
    {"name": "Alex Reyes", "company": "Delta Freight"},
    {"name": "Sam Osei", "company": "Solaris Energy"},
    {"name": "Priya Nair", "company": "Northwind Trading"},
    {"name": "Chen Wei", "company": "Vertex Energy"}
]

def filter_by_keyword(prospect_list, keyword):
    matches = []
    for prospect in prospect_list:
        if keyword.lower() in prospect["company"].lower():
            matches.append(prospect)
    return matches

energy_prospects = filter_by_keyword(prospects, "Energy")

for p in energy_prospects:
    print(p["name"], "-", p["company"])