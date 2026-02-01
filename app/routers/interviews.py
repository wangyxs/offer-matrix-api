from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.interview import (
    InterviewRecord as InterviewRecordSchema, 
    InterviewRecordCreate, 
    InterviewRecordUpdate,
    Question as QuestionSchema,
    QuestionCreate,
    QuestionUpdate,
    Favorite as FavoriteSchema,
    FavoriteCreate
)
from app.schemas.common import ResponseModel
from app.services.interview_service import (
    get_interview_record,
    get_interview_records,
    create_interview_record,
    update_interview_record,
    delete_interview_record,
    get_question,
    get_questions,
    create_question,
    update_question,
    delete_question,
    get_favorites,
    create_favorite,
    delete_favorite
)

router = APIRouter(prefix="/api/interviews", tags=["面试"])


@router.get("/", response_model=List[InterviewRecordSchema])
async def read_interview_records(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的面试记录列表"""
    records = get_interview_records(db, user_id=current_user.id, skip=skip, limit=limit)
    return records


@router.post("/", response_model=ResponseModel)
async def create_interview_record_endpoint(
    record: InterviewRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新的面试记录"""
    db_record = create_interview_record(db, record, user_id=current_user.id)
    return ResponseModel(
        success=True,
        message="面试记录创建成功",
        data={"record_id": db_record.id, "title": db_record.title}
    )


@router.get("/{record_id}", response_model=InterviewRecordSchema)
async def read_interview_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据ID获取面试记录"""
    db_record = get_interview_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    if db_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此记录"
        )
    return db_record


@router.put("/{record_id}", response_model=ResponseModel)
async def update_interview_record_endpoint(
    record_id: int,
    record_update: InterviewRecordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新面试记录"""
    db_record = get_interview_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    if db_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此记录"
        )
    
    updated_record = update_interview_record(db, record_id=record_id, record_update=record_update)
    return ResponseModel(
        success=True,
        message="面试记录更新成功",
        data={"record_id": updated_record.id, "title": updated_record.title}
    )


@router.delete("/{record_id}", response_model=ResponseModel)
async def delete_interview_record_endpoint(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除面试记录"""
    db_record = get_interview_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试记录不存在"
        )
    if db_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此记录"
        )
    
    success = delete_interview_record(db, record_id=record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="删除失败"
        )
    
    return ResponseModel(
        success=True,
        message="面试记录删除成功",
        data={"record_id": record_id}
    )


questions_router = APIRouter(prefix="/api/questions", tags=["问题"])


@questions_router.get("/", response_model=List[QuestionSchema])
async def read_questions(
    role_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取问题列表"""
    questions = get_questions(db, role_id=role_id, skip=skip, limit=limit)
    return questions


@questions_router.post("/", response_model=ResponseModel)
async def create_question_endpoint(
    question: QuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建新问题"""
    db_question = create_question(db, question)
    return ResponseModel(
        success=True,
        message="问题创建成功",
        data={"question_id": db_question.id}
    )


@questions_router.get("/{question_id}", response_model=QuestionSchema)
async def read_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取问题"""
    db_question = get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )
    return db_question


@questions_router.put("/{question_id}", response_model=ResponseModel)
async def update_question_endpoint(
    question_id: int,
    question_update: QuestionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新问题"""
    updated_question = update_question(db, question_id=question_id, question_update=question_update)
    if updated_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )
    
    return ResponseModel(
        success=True,
        message="问题更新成功",
        data={"question_id": updated_question.id}
    )


@questions_router.delete("/{question_id}", response_model=ResponseModel)
async def delete_question_endpoint(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除问题"""
    success = delete_question(db, question_id=question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="问题不存在"
        )
    
    return ResponseModel(
        success=True,
        message="问题删除成功",
        data={"question_id": question_id}
    )


favorites_router = APIRouter(prefix="/api/favorites", tags=["收藏"])


@favorites_router.get("/", response_model=List[FavoriteSchema])
async def read_favorites(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的收藏列表"""
    favorites = get_favorites(db, user_id=current_user.id, skip=skip, limit=limit)
    return favorites


@favorites_router.post("/", response_model=ResponseModel)
async def create_favorite_endpoint(
    favorite: FavoriteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加收藏"""
    favorite_data = favorite.dict()
    favorite_data["user_id"] = current_user.id
    db_favorite = create_favorite(db, FavoriteCreate(**favorite_data))
    return ResponseModel(
        success=True,
        message="收藏添加成功",
        data={"favorite_id": db_favorite.id}
    )


@favorites_router.delete("/{question_id}", response_model=ResponseModel)
async def delete_favorite_endpoint(
    question_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """取消收藏"""
    success = delete_favorite(db, user_id=current_user.id, question_id=question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏不存在"
        )
    
    return ResponseModel(
        success=True,
        message="收藏取消成功",
        data={"question_id": question_id}
    )