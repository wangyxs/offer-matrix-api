import sqlite3

conn = sqlite3.connect('offer_matrix.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='question_sets';")
print(cursor.fetchone()[0])
conn.close()
