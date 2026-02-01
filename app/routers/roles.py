from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.role import UserRole, UserRoleDocument
from app.schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate, UserRole as UserRoleSchema, UserRoleCreate
from app.schemas.common import ResponseModel
from app.services.role_service import (
    get_role, 
    get_role_by_name, 
    get_roles, 
    create_role, 
    update_role, 
    delete_role,
    get_user_roles,
    assign_role_to_user,
    remove_role_from_user
)

router = APIRouter(prefix="/api/roles", tags=["角色"])


@router.get("/", response_model=List[RoleSchema])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色列表"""
    roles = get_roles(db, skip=skip, limit=limit)
    return roles


@router.post("/", response_model=ResponseModel)
async def create_role_endpoint(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新角色"""
    # 检查角色名是否已存在
    if get_role_by_name(db, role.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色名已存在"
        )
    
    db_role = create_role(db, role)
    return ResponseModel(
        success=True,
        message="角色创建成功",
        data={"role_id": db_role.id, "name": db_role.name}
    )


@router.get("/{role_id}", response_model=RoleSchema)
async def read_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """根据ID获取角色"""
    db_role = get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    return db_role


@router.put("/{role_id}", response_model=ResponseModel)
async def update_role_endpoint(
    role_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新角色信息"""
    db_role = update_role(db, role_id=role_id, role_update=role_update)
    if db_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return ResponseModel(
        success=True,
        message="角色信息更新成功",
        data={"role_id": db_role.id, "name": db_role.name}
    )


@router.delete("/{role_id}", response_model=ResponseModel)
async def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除角色"""
    success = delete_role(db, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在"
        )
    
    return ResponseModel(
        success=True,
        message="角色删除成功",
        data={"role_id": role_id}
    )


@router.get("/user/{user_id}", response_model=List[UserRoleSchema])
async def read_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的角色列表"""
    user_roles = get_user_roles(db, user_id=user_id)
    return user_roles


@router.post("/assign", response_model=ResponseModel)
async def assign_role_to_user_endpoint(
    user_role: UserRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """为用户分配角色"""
    try:
        db_user_role = assign_role_to_user(db, user_role=user_role)
        return ResponseModel(
            success=True,
            message="角色添加成功",
            data={
                "user_role_id": db_user_role.id,
                "user_id": db_user_role.user_id,
                "role_id": db_user_role.role_id
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/remove/{user_id}/{role_id}", response_model=ResponseModel)
async def remove_role_from_user_endpoint(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """移除用户的角色"""
    # 检查用户现有角色数量
    user_roles = get_user_roles(db, user_id=user_id)
    if len(user_roles) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要保留一个角色"
        )

    success = remove_role_from_user(db, user_id=user_id, role_id=role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户角色关联不存在"
        )
    
    return ResponseModel(
        success=True,
        message="角色移除成功",
        data={"user_id": user_id, "role_id": role_id}
    )


# --- 文档管理 API ---

from app.services.rag_service import rag_service
from fastapi import File, UploadFile
import shutil
import os
import uuid
from app.core.config import settings

@router.post("/user/{role_id}/documents", response_model=ResponseModel)
async def upload_document(
    role_id: int,
    file_type: str, # RESUME or MATERIAL
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文档 (简历或学习资料)"""
    # 1. 找到对应的 UserRole 记录
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.role_id == role_id,
        UserRole.is_active == True
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=404, detail="未找到该角色的关联记录")
    
    # NEW: 单份简历限制
    if file_type == "RESUME":
        existing_resume = db.query(UserRoleDocument).filter(
            UserRoleDocument.user_role_id == user_role.id,
            UserRoleDocument.file_type == "RESUME"
        ).first()
        
        if existing_resume:
            # Delete old file
            old_file_name = existing_resume.file_url.split("/")[-1]
            old_file_path = settings.DATA_DIR / "uploads" / old_file_name
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            # Delete from RAG
            rag_service.delete_document(existing_resume.id)
            # Delete from DB
            db.delete(existing_resume)
            db.commit()

    # 2. 保存文件
    upload_dir = settings.DATA_DIR / "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 计算文件大小 string
    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    size_mb = size_bytes / (1024 * 1024)
    size_str = f"{size_mb:.1f} MB"
    
    # 3. 保存数据库记录
    # 构造完整的访问 URL (假设服务器地址为 http://192.168.5.12:8000)
    # 注意：这里硬编码了 IP，生产环境应配置域名
    file_url = f"http://192.168.5.12:8000/uploads/{unique_filename}"
    
    db_doc = UserRoleDocument(
        user_role_id=user_role.id,
        file_type=file_type,
        file_url=file_url,
        filename=file.filename,
        file_size=size_str
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # NEW: 索引文档到向量数据库
    try:
        rag_service.add_document(
            doc_id=db_doc.id, 
            role_id=role_id, # Using generic role_id for filtering, or could use user_role.id for stricter privacy
            file_path=file_path, 
            file_type=file_type
        )
    except Exception as e:
        print(f"RAG Indexing Error: {e}")
        # Non-blocking, return success anyway
    
    return ResponseModel(
        success=True,
        message="上传成功",
        data={
            "id": db_doc.id,
            "filename": db_doc.filename,
            "file_url": db_doc.file_url,
            "size": db_doc.file_size,
            "date": db_doc.uploaded_at.strftime("%Y-%m-%d")
        }
    )

@router.get("/user/{role_id}/documents")
async def get_documents(
    role_id: int,
    file_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文档列表"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.role_id == role_id,
        UserRole.is_active == True
    ).first()
    
    if not user_role:
        return []
        
    query = db.query(UserRoleDocument).filter(UserRoleDocument.user_role_id == user_role.id)
    if file_type:
        query = query.filter(UserRoleDocument.file_type == file_type)
        
    docs = query.order_by(UserRoleDocument.uploaded_at.desc()).all()
    
    return [
        {
            "id": doc.id,
            "name": doc.filename,
            "size": doc.file_size,
            "date": doc.uploaded_at.strftime("%Y-%m-%d %H:%M"),
            "url": doc.file_url
        }
        for doc in docs
    ]

@router.delete("/documents/{doc_id}", response_model=ResponseModel)
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文档"""
    doc = db.query(UserRoleDocument).filter(UserRoleDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
        
    # 验证权限
    user_role = db.query(UserRole).filter(UserRole.id == doc.user_role_id).first()
    if not user_role or user_role.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此文件")
        
    # 删除物理文件
    file_name = doc.file_url.split("/")[-1]
    file_path = settings.DATA_DIR / "uploads" / file_name
    if os.path.exists(file_path):
        os.remove(file_path)

    # NEW: 删除向量索引
    try:
        rag_service.delete_document(doc_id)
    except Exception as e:
        print(f"RAG Deletion Error: {e}")
        
    db.delete(doc)
    db.commit()
    
    return ResponseModel(success=True, message="删除成功")

@router.get("/documents/{doc_id}/content", response_model=ResponseModel)
async def get_document_content(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取文档的文本内容"""
    doc = db.query(UserRoleDocument).filter(UserRoleDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
        
    # 验证权限
    user_role = db.query(UserRole).filter(UserRole.id == doc.user_role_id).first()
    if not user_role or user_role.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此文件")
        
    # 获取本地文件路径
    file_name = doc.file_url.split("/")[-1]
    file_path = settings.DATA_DIR / "uploads" / file_name
    
    if not os.path.exists(file_path):
        return ResponseModel(success=False, message="文件在服务器上未找到")
        
    # 提取文本
    content = ""
    try:
        if doc.file_type == "RESUME" or doc.file_type == "MATERIAL":
             # Use the raw file extension to decide if it's PDF or Docx, passed to RAGService or handle here?
             # rag_service.extract_text logic handles extension.
             content = rag_service.extract_text(file_path, doc.file_type)
    except Exception as e:
        print(f"Error reading file content: {e}")
        return ResponseModel(success=False, message="无法读取文件内容")
        
    return ResponseModel(
        success=True, 
        message="获取成功", 
        data={"content": content}
    )


@router.get("/user/{role_id}/resume", response_model=ResponseModel)
async def get_user_resume_content(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户在该角色的简历内容"""
    # 1. 找到对应的 UserRole 记录
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.id,
        UserRole.role_id == role_id,
        UserRole.is_active == True
    ).first()
    
    if not user_role:
        return ResponseModel(success=False, message="未找到角色关联", data={"content": ""})
    
    # 2. 查找简历文档
    resume_doc = db.query(UserRoleDocument).filter(
        UserRoleDocument.user_role_id == user_role.id,
        UserRoleDocument.file_type == "RESUME"
    ).first()
    
    if not resume_doc:
        return ResponseModel(success=False, message="未上传简历", data={"content": ""})
        
    # 3. 读取内容 (复用逻辑)
    file_name = resume_doc.file_url.split("/")[-1]
    file_path = settings.DATA_DIR / "uploads" / file_name
    
    if not os.path.exists(file_path):
        return ResponseModel(success=False, message="简历文件丢失", data={"content": ""})
        
    content = ""
    try:
        content = rag_service.extract_text(file_path, resume_doc.file_type)
    except Exception as e:
        print(f"Error reading resume content: {e}")
        return ResponseModel(success=False, message="无法读取简历内容")
        
    return ResponseModel(
        success=True,
        message="获取成功",
        data={"content": content}
    )