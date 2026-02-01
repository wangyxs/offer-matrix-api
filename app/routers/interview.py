import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.interview import Favorite, Question, InterviewRecord
from app.models.role import Role
from app.schemas.interview import (
    ChatRequest, ChatResponse, 
    SaveInterviewRecordRequest, InterviewRecordResponse, InterviewAnalysisResult
)
from app.services.interview_analysis_service import interview_analysis_service
from app.schemas.question_set import QuestionResponse
from app.schemas.common import ResponseModel
from app.services.ai_interview_service import ai_interview_service as interview_service
from app.services.edge_tts_service import edge_tts_service
from app.core.logger import logger
import os

router = APIRouter(
    prefix="/api/interview",
    tags=["interview"],
    responses={404: {"description": "Not found"}},
)

class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-CN-XiaoyiNeural"  # 默认使用小艺声音

@router.post("/chat", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Handle interview chat interaction (Text-in, Text-out).
    """
    try:
        # In the future, we might save history to DB here using `db`
        response = interview_service.process_chat(request, db)
        return response
    except Exception as e:
        logger.error(f"Error in interview chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during the interview session: {str(e)}"
        )

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    使用 Edge TTS 将文本转换为语音
    返回 MP3 音频文件
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # 限制文本长度
        if len(request.text) > 2000:
            request.text = request.text[:2000]
        
        # 生成音频
        audio_path = edge_tts_service.generate_audio(
            text=request.text,
            voice=request.voice,
            rate="+5%"  # 稍微加快语速
        )
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename="tts_output.mp3",
            background=None  # 不在后台删除文件，让客户端下载完成
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}"
        )


# --- 收藏功能 API ---

@router.post("/favorites/{question_id}", response_model=ResponseModel)
async def add_favorite(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """收藏题目"""
    # 检查题目是否存在
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # 检查是否已收藏
    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.question_id == question_id
    ).first()
    
    if existing_favorite:
        return ResponseModel(
            success=True,
            message="该题目已收藏",
            data={"favorite_id": existing_favorite.id}
        )
    
    # 创建收藏
    favorite = Favorite(
        user_id=current_user.id,
        question_id=question_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return ResponseModel(
        success=True,
        message="收藏成功",
        data={"favorite_id": favorite.id}
    )


@router.delete("/favorites/{question_id}", response_model=ResponseModel)
async def remove_favorite(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消收藏题目"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.question_id == question_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )
    
    db.delete(favorite)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="取消收藏成功",
        data={"question_id": question_id}
    )


@router.get("/favorites", response_model=List[QuestionResponse])
async def get_favorites(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户收藏的题目列表"""
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).order_by(Favorite.created_at.desc()).offset(skip).limit(limit).all()
    
    questions = [QuestionResponse.from_orm(fav.question) for fav in favorites]
    
    return questions


@router.get("/favorites/check/{question_id}")
async def check_favorite_status(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """检查题目是否已收藏"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.question_id == question_id
    ).first()
    
    return {"is_favorited": favorite is not None}

@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个题目详情"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # Manual mapping for safety
    return QuestionResponse(
        id=question.id,
        question_text=question.question_text,
        answer_text=question.answer_text,
        difficulty=question.difficulty or "medium",
        category=question.category,
        question_style=question.question_style or "medium",
        ai_generated=bool(question.ai_generated)
    )


# --- 面试记录与分析 API ---

@router.post("/records", response_model=ResponseModel)
async def save_interview_record(
    request: SaveInterviewRecordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """保存面试记录"""
    try:
        # 获取角色名称
        role = db.query(Role).filter(Role.id == request.role_id).first()
        role_name = role.name if role else "未知岗位"
        
        # 创建面试记录
        record = InterviewRecord(
            user_id=current_user.id,
            role_id=request.role_id,
            title=request.title or f"{role_name}模拟面试",
            content=request.content,
            is_completed=False
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        logger.info(f"Interview record saved: id={record.id}, user={current_user.id}")
        
        return ResponseModel(
            success=True,
            message="面试记录保存成功",
            data={"record_id": record.id}
        )
    except Exception as e:
        logger.error(f"Failed to save interview record: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存面试记录失败: {str(e)}"
        )


@router.get("/records", response_model=List[InterviewRecordResponse])
async def get_interview_records(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户的面试记录列表"""
    records = db.query(InterviewRecord).filter(
        InterviewRecord.user_id == current_user.id
    ).order_by(InterviewRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for record in records:
        role = db.query(Role).filter(Role.id == record.role_id).first()
        result.append(InterviewRecordResponse(
            id=record.id,
            user_id=record.user_id,
            role_id=record.role_id,
            title=record.title,
            content=record.content,
            score=record.score,
            feedback=record.feedback,
            is_completed=record.is_completed,
            created_at=record.created_at,
            role_name=role.name if role else None
        ))
    
    return result


@router.get("/records/{record_id}", response_model=InterviewRecordResponse)
async def get_interview_record_detail(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取面试记录详情"""
    record = db.query(InterviewRecord).filter(
        InterviewRecord.id == record_id,
        InterviewRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    
    role = db.query(Role).filter(Role.id == record.role_id).first()
    
    return InterviewRecordResponse(
        id=record.id,
        user_id=record.user_id,
        role_id=record.role_id,
        title=record.title,
        content=record.content,
        score=record.score,
        feedback=record.feedback,
        is_completed=record.is_completed,
        created_at=record.created_at,
        role_name=role.name if role else None
    )


@router.post("/records/{record_id}/analyze", response_model=ResponseModel)
async def analyze_interview_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """使用智谱LLM分析面试记录"""
    record = db.query(InterviewRecord).filter(
        InterviewRecord.id == record_id,
        InterviewRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    
    if not record.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试记录内容为空，无法分析"
        )
    
    try:
        # 获取角色名称
        role = db.query(Role).filter(Role.id == record.role_id).first()
        role_name = role.name if role else None
        
        # 调用分析服务
        analysis_result = interview_analysis_service.analyze_interview(
            conversation=record.content,
            role_name=role_name
        )
        
        # 更新记录 - 保存完整的分析结果JSON
        record.score = analysis_result.get("score", 0)
        record.feedback = json.dumps(analysis_result, ensure_ascii=False)  # 保存完整JSON
        record.is_completed = True
        db.commit()
        
        logger.info(f"Interview analysis completed: id={record_id}, score={record.score}")
        
        return ResponseModel(
            success=True,
            message="分析完成",
            data=analysis_result
        )
    except Exception as e:
        logger.error(f"Failed to analyze interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析面试记录失败: {str(e)}"
        )


@router.delete("/records/{record_id}", response_model=ResponseModel)
async def delete_interview_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除面试记录"""
    record = db.query(InterviewRecord).filter(
        InterviewRecord.id == record_id,
        InterviewRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    
    try:
        db.delete(record)
        db.commit()
        logger.info(f"Interview record deleted: id={record_id}, user={current_user.id}")
        
        return ResponseModel(
            success=True,
            message="删除成功",
            data={"record_id": record_id}
        )
    except Exception as e:
        logger.error(f"Failed to delete interview record: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除面试记录失败: {str(e)}"
        )
