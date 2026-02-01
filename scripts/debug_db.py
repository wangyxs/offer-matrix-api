
from sqlalchemy import create_engine, text
from app.core.config import settings
from sqlalchemy.orm import sessionmaker

# Connect to DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Checking User 'wyx'...")

try:
    # 1. Get User
    result = db.execute(text("SELECT id, username FROM users WHERE username = 'wyx'"))
    user = result.fetchone()
    
    if not user:
        print("User 'wyx' not found.")
    else:
        user_id = user[0]
        print(f"User Found: ID={user_id}, Name={user[1]}")
        
        # 2. Get User Roles
        roles_res = db.execute(text(f"SELECT id, role_id FROM user_roles WHERE user_id = {user_id}"))
        user_roles = roles_res.fetchall()
        
        print(f"User Roles Count: {len(user_roles)}")
        
        for ur in user_roles:
            ur_id = ur[0]
            role_id = ur[1]
            
            # Get Role Name
            role_res = db.execute(text(f"SELECT name FROM roles WHERE id = {role_id}"))
            role_name = role_res.scalar()
            
            print(f"\nUserRole ID: {ur_id} (Role: {role_name}, ID: {role_id})")
            
            # 3. Get Documents
            docs_res = db.execute(text(f"SELECT id, file_type, filename, file_url FROM user_role_documents WHERE user_role_id = {ur_id}"))
            docs = docs_res.fetchall()
            
            if not docs:
                print("  No documents found.")
            else:
                for doc in docs:
                    print(f"  Doc ID: {doc[0]}, Type: {doc[1]}, Name: {doc[2]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
