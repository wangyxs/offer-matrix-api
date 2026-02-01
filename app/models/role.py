from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联用户角色
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联用户和角色
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
    documents = relationship("UserRoleDocument", back_populates="user_role", cascade="all, delete-orphan")


class UserRoleDocument(Base):
    __tablename__ = "user_role_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_role_id = Column(Integer, ForeignKey("user_roles.id"), nullable=False)
    file_type = Column(String(20), nullable=False) # RESUME, MATERIAL
    file_url = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(String(20), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user_role = relationship("UserRole", back_populates="documents")