from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# 题目相关Schema
class QuestionResponse(BaseModel):
    """题目详情响应"""
    id: int
    question_text: str
    answer_text: Optional[str] = None
    difficulty: str
    category: Optional[str] = None
    question_style: str
    ai_generated: bool
    
    class Config:
        from_attributes = True


# 题组相关Schema
class QuestionSetCreate(BaseModel):
    """创建题组请求"""
    role_id: int
    question_count: int  # 题目数量: 3, 5, 10
    question_style: str  # short, medium, long
    extra_requirements: Optional[str] = None  # 额外需求描述


class QuestionSetResponse(BaseModel):
    """题组响应"""
    id: int
    user_id: int
    role_id: int
    title: str
    question_count: int
    question_style: str
    extra_requirements: Optional[str] = None
    created_at: datetime
    role_name: Optional[str] = None  # 前端显示用
    is_viewed: bool = False
    
    class Config:
        from_attributes = True


class QuestionSetDetail(BaseModel):
    """题组详情(含题目列表)"""
    id: int
    user_id: int
    role_id: int
    title: str
    question_count: int
    question_style: str
    extra_requirements: Optional[str] = None
    created_at: datetime
    role_name: Optional[str] = None
    is_viewed: bool = False
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True
