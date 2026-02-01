from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Chat Schemas (New) ---
class ChatRequest(BaseModel):
    user_input: str
    target_position: str
    current_question: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = [] # [{"role": "user", "content": "..."}, ...]

class ChatResponse(BaseModel):
    reply: str  # AI Response
    action: Optional[str] = "listen" # listen / stop / finish
    history: Optional[List[Dict[str, str]]] = []
    data: Optional[Dict[str, Any]] = None

# --- CRUD Schemas (Restored) ---

# Question Schemas
class QuestionBase(BaseModel):
    content: str
    role_id: Optional[int] = None
    difficulty: Optional[str] = "medium"
    category: Optional[str] = "general"

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interview Record Schemas
class InterviewRecordBase(BaseModel):
    title: str = "Mock Interview"
    role_id: int
    duration: Optional[int] = 0
    score: Optional[int] = 0
    feedback: Optional[str] = None

class InterviewRecordCreate(InterviewRecordBase):
    pass

class InterviewRecordUpdate(InterviewRecordBase):
    pass

class InterviewRecord(InterviewRecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Favorite Schemas
class FavoriteBase(BaseModel):
    question_id: int

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# --- Interview Record Schemas (for mock interview recording) ---

class SaveInterviewRecordRequest(BaseModel):
    """保存面试记录请求"""
    role_id: int
    title: str = "模拟面试"
    content: str  # JSON格式的对话记录
    duration: int = 0  # 面试时长（秒）

class InterviewRecordResponse(BaseModel):
    """面试记录响应"""
    id: int
    user_id: int
    role_id: Optional[int]
    title: str
    content: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    is_completed: bool
    created_at: datetime
    role_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class DimensionScores(BaseModel):
    """分维度评分"""
    expression: int = 0  # 表达能力
    technical_depth: int = 0  # 技术深度
    logic: int = 0  # 逻辑思维
    communication: int = 0  # 沟通能力

class InterviewAnalysisResult(BaseModel):
    """面试分析结果"""
    score: float
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    detailed_feedback: str = ""
    dimension_scores: Optional[DimensionScores] = None