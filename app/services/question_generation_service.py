import json
from typing import List, Dict
from sqlalchemy.orm import Session
from app.services.llm_service import llm_service
from app.models.interview import Question, QuestionSet, QuestionSetQuestion
from app.models.role import Role
from app.core.logger import logger


class QuestionGenerationService:
    """AI题目生成服务"""
    
    def generate_question_set(
        self, 
        db: Session, 
        user_id: int, 
        role_id: int, 
        question_count: int, 
        question_style: str, 
        extra_requirements: str = None
    ) -> QuestionSet:
        """
        生成题组主方法
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            role_id: 角色ID
            question_count: 题目数量
            question_style: 题目风格(short/medium/long)
            extra_requirements: 额外需求
            
        Returns:
            QuestionSet: 生成的题组对象
        """
        # 1. 获取角色信息
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"角色ID {role_id} 不存在")
        
        # 2. 构建AI提示词
        prompt = self._build_prompt(role, question_count, question_style, extra_requirements)
        
        # 3. 调用LLM生成题目
        questions_data = self._call_llm_for_questions(prompt)
        
        # 4. 创建题组
        question_set = self._create_question_set(
            db, user_id, role_id, question_count, question_style, extra_requirements
        )
        
        # 5. 保存题目并关联到题组
        self._save_questions(db, question_set, role_id, questions_data)
        
        db.commit()
        db.refresh(question_set)
        
        return question_set
    
    def _build_prompt(
        self, 
        role: Role, 
        question_count: int, 
        question_style: str, 
        extra_requirements: str = None
    ) -> str:
        """构建AI生成题目的提示词"""
        
        # 风格说明
        style_descriptions = {
            "short": "短文本题目(50-100字),适合快速回答",
            "medium": "中等文本题目(100-200字),需要详细解释",
            "long": "长文本题目(200-300字以上),需要深入分析和案例说明"
        }
        style_desc = style_descriptions.get(question_style, style_descriptions["medium"])
        
        # 基础提示词
        prompt = f"""你是一位资深的面试官,专门负责 {role.name} 岗位的面试。

【岗位要求】
{role.prompt if role.prompt else role.description}

【生成任务】
请生成 {question_count} 道高质量的面试题目。

【题目要求】
1. 题目风格: {style_desc}
2. 难度分布: 适当混合简单、中等、困难题目
3. 覆盖范围: 涵盖技术深度、项目经验、问题解决能力等多个维度
4. 实战性: 题目应贴近实际工作场景
"""
        
        # 添加额外需求
        if extra_requirements and extra_requirements.strip():
            prompt += f"\n【额外要求】\n{extra_requirements}\n"
        
        # 输出格式要求
        prompt += """
【输出格式】
请以JSON数组格式返回,每道题目包含以下字段:
- question: 题目内容(string)
- answer: 参考答案(string,详细完整)
- difficulty: 难度级别(string, 可选值: easy, medium, hard)
- category: 题目类别(string, 如"算法"、"系统设计"、"项目经验"等)

示例格式:
[
  {
    "question": "请解释一下...",
    "answer": "详细答案内容...",
    "difficulty": "medium",
    "category": "基础知识"
  }
]

请确保返回的是有效的JSON格式,不要包含任何其他文字说明。
"""
        return prompt
    
    def _call_llm_for_questions(self, prompt: str) -> List[Dict]:
        """调用LLM生成题目"""
        try:
            messages = [
                {"role": "system", "content": "你是一位专业的面试官,擅长设计高质量的面试题目。请严格按照JSON格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            response = llm_service.chat_completion(messages, temperature=0.8)
            
            # 清理响应,提取JSON
            clean_json = response.replace("```json", "").replace("```", "").strip()
            questions_data = json.loads(clean_json)
            
            if not isinstance(questions_data, list):
                raise ValueError("LLM返回的不是数组格式")
            
            return questions_data
            
        except json.JSONDecodeError as e:
            logger.error(f"解析LLM响应失败: {e}, 响应内容: {response}")
            raise ValueError(f"AI生成的题目格式错误,请重试")
        except Exception as e:
            logger.exception(f"调用LLM生成题目失败: {e}")
            raise ValueError(f"生成题目时发生错误: {str(e)}")
    
    def _create_question_set(
        self, 
        db: Session, 
        user_id: int, 
        role_id: int, 
        question_count: int, 
        question_style: str, 
        extra_requirements: str = None
    ) -> QuestionSet:
        """创建题组记录"""
        # 生成题组标题
        from datetime import datetime
        timestamp = datetime.now().strftime("%m%d")
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 获取用户今天的题组数量用于编号
        existing_count = db.query(QuestionSet).filter(
            QuestionSet.user_id == user_id,
            QuestionSet.created_at >= today_start
        ).count()
        
        title = f"题组 #{timestamp}-{str(existing_count + 1).zfill(3)}"  # 1024-001, 1024-002, etc.
        
        question_set = QuestionSet(
            user_id=user_id,
            role_id=role_id,
            title=title,
            question_count=question_count,
            question_style=question_style,
            extra_requirements=extra_requirements
        )
        
        db.add(question_set)
        db.flush()  # 获取ID但不提交
        
        return question_set
    
    def _save_questions(
        self, 
        db: Session, 
        question_set: QuestionSet, 
        role_id: int, 
        questions_data: List[Dict]
    ):
        """保存题目并关联到题组"""
        for index, q_data in enumerate(questions_data):
            # 创建题目
            question = Question(
                role_id=role_id,
                question_text=q_data.get("question", ""),
                answer_text=q_data.get("answer", ""),
                difficulty=str(q_data.get("difficulty", "medium"))[:20],
                category=q_data.get("category", "综合")[:50],
                question_style=question_set.question_style,
                ai_generated=True,
                is_active=True
            )
            db.add(question)
            db.flush()  # 获取question.id
            
            # 创建关联
            association = QuestionSetQuestion(
                question_set_id=question_set.id,
                question_id=question.id,
                order_index=index
            )
            db.add(association)


question_generation_service = QuestionGenerationService()
