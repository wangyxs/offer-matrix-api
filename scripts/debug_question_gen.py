import logging
import sys
from app.core.database import SessionLocal
from app.services.question_generation_service import question_generation_service
from app.models.user import User

# Setup basic logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

db = SessionLocal()

# Mock user and role
user_id = 1
role_id = 1 # Java Architect
question_count = 5
question_style = "medium"
extra_requirements = ""

print("Starting generation...")
try:
    result = question_generation_service.generate_question_set(
        db=db,
        user_id=user_id,
        role_id=role_id,
        question_count=question_count,
        question_style=question_style,
        extra_requirements=extra_requirements
    )
    print("Generation successful!")
    print(f"ID: {result.id}, Title: {result.title}")
except Exception as e:
    logger.exception("Generation failed!")
    print(f"Error: {e}")
