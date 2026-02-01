import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('offer_matrix.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE roles ADD COLUMN category VARCHAR(50)")
        conn.commit()
        print("Migration successful: Added category column to roles table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Migration skipped: Column category already exists.")
        else:
            print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
