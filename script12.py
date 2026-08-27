import sqlite3
def search_prospects(keyword):
    conn = sqlite3.connect("prospects.db")
    cursor = conn.cursor()
    cursor.execute("SELECT scores FROM prospects WHERE company LIKE ?", (f%{keyword}%,))
    results = cursor.fetchall()
    conn.close()
    return results

for row in search_prospects("Energy"):
    print(row)