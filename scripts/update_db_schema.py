import sqlite3

conn = sqlite3.connect('offer_matrix.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE questions ADD COLUMN question_style VARCHAR(20) DEFAULT 'medium';")
    print("Added question_style column.")
except Exception as e:
    print(f"Error adding question_style: {e}")

try:
    cursor.execute("ALTER TABLE questions ADD COLUMN ai_generated BOOLEAN DEFAULT 0;")
    print("Added ai_generated column.")
except Exception as e:
    print(f"Error adding ai_generated: {e}")

conn.commit()
conn.close()
