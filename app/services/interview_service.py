from sqlalchemy.orm import Session
from app.models.interview import InterviewRecord, Question, Favorite
from app.schemas.interview import (
    InterviewRecordCreate, 
    InterviewRecordUpdate, 
    QuestionCreate, 
    QuestionUpdate,
    FavoriteCreate
)
from typing import List, Optional

# --- Interview Records ---

def get_interview_records(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[InterviewRecord]:
    return db.query(InterviewRecord).filter(InterviewRecord.user_id == user_id).offset(skip).limit(limit).all()

def create_interview_record(db: Session, record: InterviewRecordCreate, user_id: int) -> InterviewRecord:
    db_record = InterviewRecord(**record.dict(), user_id=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_interview_record(db: Session, record_id: int) -> Optional[InterviewRecord]:
    return db.query(InterviewRecord).filter(InterviewRecord.id == record_id).first()

def update_interview_record(db: Session, record_id: int, record_update: InterviewRecordUpdate) -> InterviewRecord:
    db_record = get_interview_record(db, record_id)
    if not db_record:
        return None
    
    update_data = record_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_interview_record(db: Session, record_id: int) -> bool:
    db_record = get_interview_record(db, record_id)
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True

# --- Questions ---

def get_questions(db: Session, role_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Question]:
    query = db.query(Question)
    if role_id:
        query = query.filter(Question.role_id == role_id)
    return query.offset(skip).limit(limit).all()

def create_question(db: Session, question: QuestionCreate) -> Question:
    db_question = Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_question(db: Session, question_id: int) -> Optional[Question]:
    return db.query(Question).filter(Question.id == question_id).first()

def update_question(db: Session, question_id: int, question_update: QuestionUpdate) -> Question:
    db_question = get_question(db, question_id)
    if not db_question:
        return None
    
    update_data = question_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_question, key, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    db_question = get_question(db, question_id)
    if not db_question:
        return False
    
    db.delete(db_question)
    db.commit()
    return True

# --- Favorites ---

def get_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Favorite]:
    return db.query(Favorite).filter(Favorite.user_id == user_id).offset(skip).limit(limit).all()

def create_favorite(db: Session, favorite: FavoriteCreate) -> Favorite:
    db_favorite = Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def delete_favorite(db: Session, user_id: int, question_id: int) -> bool:
    db_favorite = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.question_id == question_id).first()
    if not db_favorite:
        return False
    
    db.delete(db_favorite)
    db.commit()
    return True