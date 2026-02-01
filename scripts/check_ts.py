import sqlite3
import json

def check_timestamps():
    conn = sqlite3.connect('D:/Desktop/OfferMatrix_Project/offer-matrix-backend/backend/offer_matrix.db')
    cursor = conn.cursor()
    cursor.execute("SELECT created_at FROM interview_records ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Database value: {row[0]}")
    else:
        print("No records found.")
    conn.close()

if __name__ == "__main__":
    check_timestamps()
