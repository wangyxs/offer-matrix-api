"""
数据库迁移脚本: 添加题组相关表

运行方式:
python create_question_sets_tables.py
"""

from app.core.database import engine, Base
from app.models.interview import QuestionSet, QuestionSetQuestion, Question, Favorite
from app.models.user import User
from app.models.role import Role


def create_tables():
    """创建新增的数据库表"""
    print("开始创建题组相关表...")
    
    # 这将创建所有继承自Base的表(如果不存在)
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表创建完成!")
    print("新增的表:")
    print("  - question_sets (题组表)")
    print("  - question_set_questions (题组-题目关联表)")
    print("\n更新的表:")
    print("  - questions (添加了 question_style 和 ai_generated 字段)")


if __name__ == "__main__":
    create_tables()
