import sqlite3
from pathlib import Path

def check_timestamps():
    db_path = Path(__file__).resolve().parents[1] / "offer_matrix.db"
    conn = sqlite3.connect(db_path)
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
