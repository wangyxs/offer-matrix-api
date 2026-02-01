import sys
from app.core.database import SessionLocal
from app.models.user import User
from app.models.interview import QuestionSet, QuestionSetQuestion, Question

db = SessionLocal()

# 1. Find user
user = db.query(User).filter(User.username == "wyx").first()
if not user:
    print("User 'wyx' not found!")
    sys.exit(1)

print(f"User Found: ID={user.id}, Username={user.username}")

# 2. Find QuestionSets
q_sets = db.query(QuestionSet).filter(QuestionSet.user_id == user.id).all()
print(f"Found {len(q_sets)} QuestionSets")

for qs in q_sets:
    print(f"\n[QuestionSet ID={qs.id}] Title='{qs.title}', Style='{qs.question_style}'")
    
    # 3. Find Questions
    associations = db.query(QuestionSetQuestion).filter(QuestionSetQuestion.question_set_id == qs.id).all()
    print(f"  -> Contains {len(associations)} questions")
    
    for assoc in associations:
        q = assoc.question
        print(f"    [QID={q.id}] Diff='{q.difficulty}', Cat='{q.category}'")
        print(f"      Text (first 50): {q.question_text[:50]!r}")
        print(f"      Answer (first 50): {q.answer_text[:50]!r}")
        # Check for potential format issues
        if q.question_text.strip().startswith("{") or q.question_text.strip().startswith("["):
             print("      WARNING: Text looks like JSON!")
