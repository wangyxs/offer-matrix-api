from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.role import Role, UserRole
from app.models.user import User

def reset_roles():
    db = SessionLocal()
    try:
        # Delete all user_roles first to avoid FK constraints
        db.query(UserRole).delete()
        
        # Delete all existing roles
        db.query(Role).delete()
        
        # Commit deletion
        db.commit()
        print("已清除旧角色数据")
        
        # Add new roles
        roles_data = [
            {
                "name": "Java 架构师",
                "category": "后端",
                "description": "负责设计和搭建高可用、高性能的 Java 后端系统，精通并发编程、JVM 调优和微服务架构。",
                "prompt": "你现在是一位经验丰富的 Java 架构师面试官。请针对 Java 并发编程、JVM 原理、Spring Cloud 微服务架构以及分布式系统设计等方面进行提问。注重考察候选人的系统设计能力和深度技术理解。"
            },
            {
                "name": "前端技术专家",
                "category": "前端",
                "description": "负责复杂前端应用的架构设计与开发，精通 React/Vue 生态、前端工程化及性能优化。",
                "prompt": "你现在是一位资深的前端技术专家面试官。请重点考察 JavaScript 核心原理、浏览器渲染机制、React/Vue 源码实现、前端工程化建设以及性能优化方案。同时关注候选人的代码质量和组件设计能力。"
            },
            {
                "name": "AI 算法工程师",
                "category": "AI",
                "description": "负责深度学习模型的训练与部署，熟悉 PyTorch/TensorFlow，在大模型或 CV/NLP 领域有深入研究。",
                "prompt": "你现在是一位 AI 算法工程师面试官。请重点考察机器学习基础理论、深度学习框架（PyTorch/TensorFlow）的使用、Transformer 架构细节以及大模型（LLM）的微调与应用。关注候选人的学术背景和工程落地能力。"
            },
            {
                "name": "产品经理",
                "category": "产品",
                "description": "负责互联网产品的规划与设计，具备敏锐的市场洞察力和优秀的需求分析能力。",
                "prompt": "你现在是一位资深产品经理面试官。请围绕用户需求挖掘、竞品分析、产品规划（Roadmap）、交互设计以及数据驱动决策等方面进行提问。考察候选人的逻辑思维和商业敏感度。"
            },
            {
                "name": "测试工程师",
                "category": "测试",
                "description": "负责软件质量保障，熟悉自动化测试框架、性能测试及持续集成流程。",
                "prompt": "你现在是一位资深测试工程师面试官。请针对软件测试理论、自动化测试框架（如 Selenium/Appium/Pytest）、性能测试（JMeter/LoadRunner）以及 CI/CD 流程进行提问。考察候选人的质量意识和问题定位能力。"
            },
            {
                "name": "运维工程师",
                "category": "运维",
                "description": "负责系统稳定性保障，精通 Linux、Docker/K8s、监控告警及故障排查。",
                "prompt": "你现在是一位资深运维工程师（SRE）面试官。请围绕 Linux 系统管理、容器化技术（Docker/Kubernetes）、微服务监控（Prometheus/Grafana）、CI/CD 以及故障排查流程进行提问。考察候选人的系统维护能力和自动化运维思维。"
            },
        ]
        
        for role_item in roles_data:
            role = Role(
                name=role_item["name"],
                category=role_item["category"],
                description=role_item["description"],
                prompt=role_item["prompt"]
            )
            db.add(role)
        
        db.commit()
        print("新角色数据创建成功")
        
    except Exception as e:
        print(f"Error resetting roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_roles()
