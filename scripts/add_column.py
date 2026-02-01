import sqlite3

def add_column():
    conn = sqlite3.connect('d:/Desktop/OfferMatrix_Project/offer-matrix-backend/backend/offer_matrix.db')
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
