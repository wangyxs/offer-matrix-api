from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.interview import QuestionSet, QuestionSetQuestion, Question
from app.schemas.question_set import QuestionSetCreate, QuestionSetResponse, QuestionSetDetail, QuestionResponse
from app.schemas.common import ResponseModel
from app.services.question_generation_service import question_generation_service
from app.core.logger import logger


router = APIRouter(prefix="/api/question-sets", tags=["题组管理"])


@router.post("/generate", response_model=ResponseModel)
def generate_question_set(
    request: QuestionSetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """生成AI题组"""
    try:
        question_set = question_generation_service.generate_question_set(
            db=db,
            user_id=current_user.id,
            role_id=request.role_id,
            question_count=request.question_count,
            question_style=request.question_style,
            extra_requirements=request.extra_requirements
        )
        
        return ResponseModel(
            success=True,
            message="题组生成成功",
            data={
                "question_set_id": question_set.id,
                "title": question_set.title,
                "question_count": question_set.question_count
            }
        )
    except ValueError as e:
        logger.error(f"生成题组失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"生成题组时发生错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成题组失败: {str(e)}"
        )


@router.get("/", response_model=List[QuestionSetResponse])
async def get_question_sets(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的题组列表"""
    question_sets = db.query(QuestionSet).filter(
        QuestionSet.user_id == current_user.id
    ).order_by(QuestionSet.created_at.desc()).offset(skip).limit(limit).all()
    
    # 添加角色名称
    result = []
    for qs in question_sets:
        qs_dict = {
            "id": qs.id,
            "user_id": qs.user_id,
            "role_id": qs.role_id,
            "title": qs.title,
            "question_count": qs.question_count,
            "question_style": qs.question_style or "medium", # Handle None
            "extra_requirements": qs.extra_requirements,
            "created_at": qs.created_at,
            "role_name": qs.role.name if qs.role else "未知角色",
            "is_viewed": qs.is_viewed or False
        }
        result.append(QuestionSetResponse(**qs_dict))
    
    return result


@router.get("/{set_id}", response_model=QuestionSetDetail)
async def get_question_set_detail(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取题组详情(包含所有题目)"""
    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id,
        QuestionSet.user_id == current_user.id
    ).first()
    
    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题组不存在"
        )
    
    # 获取题组中的所有题目(按顺序)
    associations = db.query(QuestionSetQuestion).filter(
        QuestionSetQuestion.question_set_id == set_id
    ).order_by(QuestionSetQuestion.order_index).all()
    
    questions = []
    for assoc in associations:
        q = assoc.question
        # Handle potential nulls or missing fields gracefully
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
    
    # 构建响应
    # Manual mapping to avoid validation errors on legacy data
    result = {
        "id": question_set.id,
        "user_id": question_set.user_id,
        "role_id": question_set.role_id,
        "title": question_set.title,
        "question_count": question_set.question_count,
        "question_style": question_set.question_style or "medium",
        "extra_requirements": question_set.extra_requirements,
        "created_at": question_set.created_at,
        "role_name": question_set.role.name if question_set.role else "未知角色",
        "is_viewed": True, # Mark as viewed when details are fetched
        "questions": questions
    }
    
    # Mark as viewed in DB if not already
    if not question_set.is_viewed:
        question_set.is_viewed = True
        db.commit()
    
    return QuestionSetDetail(**result)


@router.delete("/{set_id}", response_model=ResponseModel)
async def delete_question_set(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除题组"""
    question_set = db.query(QuestionSet).filter(
        QuestionSet.id == set_id,
        QuestionSet.user_id == current_user.id
    ).first()
    
    if not question_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题组不存在"
        )
    
    db.delete(question_set)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="题组删除成功",
        data={"question_set_id": set_id}
    )
