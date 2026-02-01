import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('offer_matrix.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(255)")
        conn.commit()
        print("Migration successful: Added avatar column to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Migration skipped: Column avatar already exists.")
        else:
            print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
