import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.models.interview import QuestionSet, QuestionSetQuestion
from app.schemas.question_set import QuestionSetDetail, QuestionSetResponse, QuestionResponse

db = SessionLocal()

user = db.query(User).filter(User.username == "wyx").first()
if not user:
    print("User not found")
    sys.exit(1)

print(f"Checking data for User: {user.username} (ID={user.id})")

# Check List Endpoint logic
print("\n--- Checking List Endpoint Logic ---")
q_sets = db.query(QuestionSet).filter(QuestionSet.user_id == user.id).all()
for qs in q_sets:
    try:
        # Manual mapping as per my fix
        qs_dict = {
            "id": qs.id,
            "user_id": qs.user_id,
            "role_id": qs.role_id,
            "title": qs.title,
            "question_count": qs.question_count,
            "question_style": qs.question_style or "medium",
            "extra_requirements": qs.extra_requirements,
            "created_at": qs.created_at,
            "role_name": qs.role.name if qs.role else "未知角色"
        }
        QuestionSetResponse(**qs_dict)
        print(f"List Item ID={qs.id} OK")
    except Exception as e:
        print(f"List Item ID={qs.id} FAILED: {e}")

# Check Detail Endpoint logic
print("\n--- Checking Detail Endpoint Logic ---")
for qs in q_sets:
    print(f"Checking Detail for Set ID={qs.id}...")
    try:
        associations = db.query(QuestionSetQuestion).filter(
            QuestionSetQuestion.question_set_id == qs.id
        ).order_by(QuestionSetQuestion.order_index).all()
        
        questions = []
        for i, assoc in enumerate(associations):
            q = assoc.question
            try:
                q_dto = QuestionResponse(
                    id=q.id,
                    question_text=q.question_text,
                    answer_text=q.answer_text,
                    difficulty=q.difficulty or "medium",
                    category=q.category,
                    question_style=q.question_style or "medium",
                    ai_generated=bool(q.ai_generated)
                )
                questions.append(q_dto)
            except Exception as e:
                print(f"  Question ID={q.id} (Index {i}) FAILED construction: {e}")
                raise e
        
        # Final construction
        # result = QuestionSetDetail.from_orm(qs).dict()
        result = {
            "id": qs.id,
            "user_id": qs.user_id,
            "role_id": qs.role_id,
            "title": qs.title,
            "question_count": qs.question_count,
            "question_style": qs.question_style or "medium",
            "extra_requirements": qs.extra_requirements,
            "created_at": qs.created_at,
            "role_name": qs.role.name if qs.role else "未知角色",
            "questions": questions
        }
        
        QuestionSetDetail(**result)
        print(f"Detail Set ID={qs.id} OK")
        
    except Exception as e:
        print(f"Detail Set ID={qs.id} FAILED: {e}")
