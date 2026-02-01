#!/usr/bin/env python3
"""
数据库初始化脚本
"""

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import User, Role, UserRole, InterviewRecord, Question, Favorite
from app.core.security import get_password_hash

def init_db():
    """初始化数据库"""
    # 创建所有表
    User.metadata.create_all(bind=engine)
    Role.metadata.create_all(bind=engine)
    UserRole.metadata.create_all(bind=engine)
    InterviewRecord.metadata.create_all(bind=engine)
    Question.metadata.create_all(bind=engine)
    Favorite.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # 检查是否已有角色数据
        if db.query(Role).count() == 0:
            # 创建默认角色
            roles_data = [
                {
                    "name": "Java 架构师",
                    "description": "负责设计和搭建高可用、高性能的 Java 后端系统，精通并发编程、JVM 调优和微服务架构。",
                    "prompt": "你现在是一位经验丰富的 Java 架构师面试官。请针对 Java 并发编程、JVM 原理、Spring Cloud 微服务架构以及分布式系统设计等方面进行提问。注重考察候选人的系统设计能力和深度技术理解。"
                },
                {
                    "name": "前端技术专家",
                    "description": "负责复杂前端应用的架构设计与开发，精通 React/Vue 生态、前端工程化及性能优化。",
                    "prompt": "你现在是一位资深的前端技术专家面试官。请重点考察 JavaScript 核心原理、浏览器渲染机制、React/Vue 源码实现、前端工程化建设以及性能优化方案。同时关注候选人的代码质量和组件设计能力。"
                },
                {
                    "name": "Full Stack Developer",
                    "description": "全栈开发工程师，能够独立完成前后端开发任务，熟悉现代 Web 技术栈。",
                    "prompt": "You are a Senior Full Stack Developer interviewer. Please ask questions covering both frontend (React/Vue) and backend (Node.js/Python/Java) technologies. Focus on RESTful API design, database modeling, authentication, and deployment workflows."
                },
                {
                    "name": "AI 算法工程师",
                    "description": "负责深度学习模型的训练与部署，熟悉 PyTorch/TensorFlow，在大模型或 CV/NLP 领域有深入研究。",
                    "prompt": "你现在是一位 AI 算法工程师面试官。请重点考察机器学习基础理论、深度学习框架（PyTorch/TensorFlow）的使用、Transformer 架构细节以及大模型（LLM）的微调与应用。关注候选人的学术背景和工程落地能力。"
                },
                {
                    "name": "产品经理",
                    "description": "负责互联网产品的规划与设计，具备敏锐的市场洞察力和优秀的需求分析能力。",
                    "prompt": "你现在是一位资深产品经理面试官。请围绕用户需求挖掘、竞品分析、产品规划（Roadmap）、交互设计以及数据驱动决策等方面进行提问。考察候选人的逻辑思维和商业敏感度。"
                },
            ]
            
            for role_item in roles_data:
                role = Role(
                    name=role_item["name"],
                    description=role_item["description"],
                    prompt=role_item["prompt"]
                )
                db.add(role)
            
            db.commit()
            print("默认角色创建成功")
        
        # 检查是否已有管理员用户
        if db.query(User).filter(User.username == "admin").first() is None:
            # 创建管理员用户
            admin_user = User(
                username="admin",
                email="admin@offermatrix.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("管理员用户创建成功 (用户名: admin, 密码: admin123)")
        
        print("数据库初始化完成")
    
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()