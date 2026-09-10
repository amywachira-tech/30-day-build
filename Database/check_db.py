import sqlite3

conn = sqlite3.connect("voygr.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM accounts;")
print("Accounts:", cursor.fetchall())

cursor.execute("SELECT * FROM interactions;")
print("Interactions:", cursor.fetchall())

conn.close()