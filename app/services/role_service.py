from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.role import Role, UserRole
from app.schemas.role import RoleCreate, RoleUpdate, UserRoleCreate


def get_role(db: Session, role_id: int):
    """根据ID获取角色"""
    return db.query(Role).filter(Role.id == role_id).first()


def get_role_by_name(db: Session, name: str):
    """根据名称获取角色"""
    return db.query(Role).filter(Role.name == name).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    """获取角色列表"""
    return db.query(Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: RoleCreate):
    """创建新角色"""
    db_role = Role(
        name=role.name,
        description=role.description
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def update_role(db: Session, role_id: int, role_update: RoleUpdate):
    """更新角色信息"""
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        return None
    
    update_data = role_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: int):
    """删除角色"""
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        return False
    
    db.delete(db_role)
    db.commit()
    return True


def get_user_roles(db: Session, user_id: int):
    """获取用户的角色列表"""
    return db.query(UserRole).filter(UserRole.user_id == user_id).all()


def assign_role_to_user(db: Session, user_role: UserRoleCreate):
    """为用户分配角色"""
    # 检查用户是否已经拥有该角色
    existing_role = db.query(UserRole).filter(
        UserRole.user_id == user_role.user_id,
        UserRole.role_id == user_role.role_id
    ).first()
    
    if existing_role:
        raise ValueError("该角色已存在，不能重复添加")
    
    db_user_role = UserRole(
        user_id=user_role.user_id,
        role_id=user_role.role_id
    )
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role


def remove_role_from_user(db: Session, user_id: int, role_id: int):
    """移除用户的角色"""
    db_user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()
    
    if not db_user_role:
        return False
    
    db.delete(db_user_role)
    db.commit()
    return True