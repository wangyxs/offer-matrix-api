import sqlite3
import os

def migrate():
    try:
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            print("Created uploads directory.")

        conn = sqlite3.connect('offer_matrix.db')
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_role_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_role_id INTEGER NOT NULL,
            file_type VARCHAR(20) NOT NULL,
            file_url VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_size VARCHAR(20),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_role_id) REFERENCES user_roles (id) ON DELETE CASCADE
        )
        """)
        
        conn.commit()
        print("Migration successful: Created user_role_documents table.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
