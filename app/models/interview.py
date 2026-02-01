from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class InterviewRecord(Base):
    __tablename__ = "interview_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联用户和角色
    user = relationship("User")
    role = relationship("Role")


class QuestionSet(Base):
    """题组模型"""
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    title = Column(String(100), nullable=False)  # e.g., "题组 #1024-A"
    question_count = Column(Integer, default=0)
    question_style = Column(String(20), default="medium")  # short, medium, long
    extra_requirements = Column(Text, nullable=True)  # 用户额外需求
    is_viewed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    user = relationship("User")
    role = relationship("Role")
    questions = relationship("QuestionSetQuestion", back_populates="question_set", cascade="all, delete-orphan")


class QuestionSetQuestion(Base):
    """题组-题目关联表"""
    __tablename__ = "question_set_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    order_index = Column(Integer, default=0)  # 题目在题组中的顺序
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联
    question_set = relationship("QuestionSet", back_populates="questions")
    question = relationship("Question")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    category = Column(String(50), nullable=True)
    question_style = Column(String(20), default="medium")  # short, medium, long - 题目长度风格
    ai_generated = Column(Boolean, default=False)  # 是否AI生成
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联角色
    role = relationship("Role")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联用户和问题
    user = relationship("User")
    question = relationship("Question")