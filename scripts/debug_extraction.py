
from sqlalchemy import create_engine, text
from app.core.config import settings
from sqlalchemy.orm import sessionmaker
import os
import PyPDF2

# Connect to DB
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Debugging Resume Extraction...")

try:
    # 1. Get Resume Doc for User 'wyx' Role '产品经理'
    # db value from prev run: UserRole ID 6
    doc_res = db.execute(text("SELECT id, filename, file_url, file_type FROM user_role_documents WHERE user_role_id = 6 AND file_type = 'RESUME'"))
    doc = doc_res.fetchone()
    
    if not doc:
        print("Doc not found via query.")
    else:
        file_url = doc[2]
        print(f"File URL: {file_url}")
        
        # Extract local filename from URL
        # URL format: http://.../uploads/UUID.pdf
        unique_filename = file_url.split("/")[-1]
        file_path = os.path.join("uploads", unique_filename)
        
        print(f"Local Path: {file_path}")
        
        if not os.path.exists(file_path):
            print("ERROR: File does not exist on disk!")
        else:
            print(f"File exists. Size: {os.path.getsize(file_path)} bytes")
            
            # Try Extract Text
            print("Attempting Extraction...")
            text_content = ""
            try:
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    print(f"PDF Pages: {len(pdf_reader.pages)}")
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content += extracted + "\n"
            except Exception as ex:
                print(f"Extraction Exception: {ex}")
                
            print(f"Extracted Length: {len(text_content)}")
            print(f"Content Preview: {text_content[:100]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
