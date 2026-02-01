from sqlalchemy import text
from app.core.database import engine

def add_prompt_column():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE roles ADD COLUMN prompt TEXT"))
            conn.commit()
            print("Successfully added prompt column to roles table")
        except Exception as e:
            print(f"Error adding column (might already exist): {e}")

if __name__ == "__main__":
    add_prompt_column()
