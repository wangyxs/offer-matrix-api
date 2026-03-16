import sqlite3
from pathlib import Path

def add_column():
    db_path = Path(__file__).resolve().parents[1] / "offer_matrix.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE question_sets ADD COLUMN is_viewed BOOLEAN DEFAULT 0")
        print("Column 'is_viewed' added successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error (might already exist): {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
