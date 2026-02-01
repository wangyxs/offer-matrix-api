import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'offer_matrix.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

users_to_delete = ['user', 'test']

for username in users_to_delete:
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        user_id = result[0]
        print(f"Found user: {username} (ID: {user_id})")
        
        # 1. 删除用户角色关联
        cursor.execute("SELECT id FROM user_roles WHERE user_id = ?", (user_id,))
        user_role_ids = [row[0] for row in cursor.fetchall()]
        
        if user_role_ids:
            print(f"  Found {len(user_role_ids)} user_roles")
            
            for ur_id in user_role_ids:
                # 删除用户角色文档（简历、学习资料）
                cursor.execute("SELECT id, file_url FROM user_role_documents WHERE user_role_id = ?", (ur_id,))
                docs = cursor.fetchall()
                if docs:
                    print(f"    Deleting {len(docs)} documents for user_role {ur_id}")
                    cursor.execute("DELETE FROM user_role_documents WHERE user_role_id = ?", (ur_id,))
            
            cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))
            print(f"  Deleted {len(user_role_ids)} user_roles")
        
        # 2. 删除面试记录
        cursor.execute("SELECT id FROM interview_records WHERE user_id = ?", (user_id,))
        interview_ids = [row[0] for row in cursor.fetchall()]
        
        if interview_ids:
            print(f"  Found {len(interview_ids)} interview records")
            cursor.execute("DELETE FROM interview_records WHERE user_id = ?", (user_id,))
            print(f"  Deleted {len(interview_ids)} interview records")
        
        # 3. 删除题组（关联的题目会自动删除）
        cursor.execute("SELECT id FROM question_sets WHERE user_id = ?", (user_id,))
        question_set_ids = [row[0] for row in cursor.fetchall()]
        
        if question_set_ids:
            print(f"  Found {len(question_set_ids)} question sets")
            cursor.execute("DELETE FROM question_sets WHERE user_id = ?", (user_id,))
            print(f"  Deleted {len(question_set_ids)} question sets (and associated questions)")
        
        # 4. 删除收藏
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE user_id = ?", (user_id,))
        favorite_count = cursor.fetchone()[0]
        
        if favorite_count > 0:
            cursor.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
            print(f"  Deleted {favorite_count} favorites")
        
        # 5. 删除用户
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        print(f"Deleted user: {username} (ID: {user_id})")
    else:
        print(f"User not found: {username}")

conn.commit()
conn.close()
print("\nDeletion completed successfully!")
