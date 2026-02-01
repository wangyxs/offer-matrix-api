"""
面试分析服务

使用智谱LLM对面试对话进行分析，提供评分和反馈。
"""
import json
import logging
from typing import Optional, Dict, Any, List
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class InterviewAnalysisService:
    """面试分析服务"""
    
    def __init__(self):
        self.llm = llm_service
    
    def _preprocess_conversation(self, conversation: str) -> str:
        """
        预处理对话记录，将原始JSON转换为可读的对话格式
        
        处理的情况：
        1. 正常格式: [{"role": "user", "content": "xxx"}, {"role": "assistant", "content": "yyy"}]
        2. 分片格式: [{"role": "assistant", "content": "你"}, {"role": "assistant", "content": "好"}...]
        3. 带元数据格式: [{"content": "xxx", "question_id": "...", "reply_id": "..."}]
        """
        try:
            data = json.loads(conversation)
            if not isinstance(data, list):
                return conversation
            
            # 合并连续相同角色的消息
            merged_turns = []
            current_role = None
            current_content = []
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                # 获取内容
                content = item.get("content", "")
                if not content:
                    continue
                
                # 确定角色 (有些记录可能没有role字段)
                role = item.get("role", "")
                if not role:
                    # 如果有question_id/reply_id，说明是AI回复
                    if "question_id" in item or "reply_id" in item:
                        role = "assistant"
                    else:
                        role = "user"
                
                # 如果角色相同，合并内容
                if role == current_role:
                    current_content.append(content)
                else:
                    # 保存之前的轮次
                    if current_role and current_content:
                        merged_turns.append({
                            "role": current_role,
                            "content": "".join(current_content)
                        })
                    # 开始新的轮次
                    current_role = role
                    current_content = [content]
            
            # 保存最后一个轮次
            if current_role and current_content:
                merged_turns.append({
                    "role": current_role,
                    "content": "".join(current_content)
                })
            
            # 格式化为可读文本
            formatted_lines = []
            for turn in merged_turns:
                role_label = "候选人" if turn["role"] == "user" else "面试官"
                content = turn["content"].strip()
                if content:
                    formatted_lines.append(f"{role_label}: {content}")
            
            result = "\n\n".join(formatted_lines)
            logger.info(f"Preprocessed conversation: {len(data)} items -> {len(merged_turns)} turns")
            return result
            
        except json.JSONDecodeError:
            logger.warning("Conversation is not valid JSON, using as-is")
            return conversation
        except Exception as e:
            logger.error(f"Failed to preprocess conversation: {e}")
            return conversation
    
    def analyze_interview(
        self, 
        conversation: str, 
        role_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析面试对话
        
        Args:
            conversation: 面试对话内容（JSON格式的对话记录）
            role_name: 面试岗位名称（可选）
        
        Returns:
            分析结果字典，包含评分、优点、不足、建议等
        """
        try:
            # 预处理对话记录
            processed_conversation = self._preprocess_conversation(conversation)
            logger.info(f"Processed conversation preview: {processed_conversation[:500]}...")
            
            # 检查是否有有效内容
            if not processed_conversation.strip() or processed_conversation == "[]":
                logger.warning("Empty conversation, returning minimal result")
                return self._get_fallback_result("对话内容为空")
            
            # 构造分析提示词
            prompt = self._build_analysis_prompt(processed_conversation, role_name)
            
            # 调用智谱LLM进行分析
            messages = [
                {
                    "role": "system",
                    "content": "你是一位资深的技术面试官和职业导师。请根据面试对话记录，给出专业、具体、有建设性的分析反馈。请用JSON格式返回分析结果。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            response = self.llm.chat_completion(messages, temperature=0.5)
            
            # 调试：打印LLM原始返回
            logger.info(f"LLM raw response: {response[:500]}...")
            
            # 解析LLM返回的JSON
            result = self._parse_analysis_result(response)
            
            # 调试：打印解析后的维度分数
            dim_scores = result.get('dimension_scores', {})
            logger.info(f"Parsed dimension_scores: {dim_scores}")
            
            logger.info(f"Interview analysis completed, score: {result.get('score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze interview: {e}")
            return self._get_fallback_result(str(e))
    
    def _build_analysis_prompt(
        self, 
        conversation: str, 
        role_name: Optional[str]
    ) -> str:
        """构造分析提示词"""
        role_context = f"面试岗位：{role_name}\n" if role_name else ""
        
        prompt = f"""你是一位经验丰富的面试官。请根据以下面试对话内容，对候选人进行专业评估。

{role_context}
【面试对话记录】
{conversation}

【重要提示】
⚠️ 你必须根据上述对话的实际内容进行分析和评分，给出客观、真实的评价。
⚠️ 所有分数必须基于候选人在对话中的具体表现，不能使用固定分数。
⚠️ 每个维度的分数必须不同，体现候选人在不同方面的差异化表现。
⚠️ 要敢于打低分，真实反映候选人的实际水平，不要给出"安慰性"分数。

【输出格式】
请严格按照以下JSON格式返回（注意：下面的分数只是格式示例，你必须根据实际对话内容给出真实评分）：

{{
    "score": <根据整体表现给出0-100之间的分数>,
    "strengths": ["<具体的表现亮点1>", "<具体的表现亮点2>"],
    "weaknesses": ["<具体的不足之处1>", "<具体的不足之处2>"],
    "suggestions": ["<针对性改进建议1>", "<针对性改进建议2>"],
    "detailed_feedback": "<30字左右的总体评价>",
    "dimension_scores": {{
        "logic_expression": <逻辑表达分数>,
        "technical_depth": <技术深度分数>,
        "stability": <稳定性分数>,
        "solution_ability": <方案能力分数>,
        "stress_resistance": <抗压能力分数>,
        "communication": <沟通技巧分数>
    }}
}}

【维度评分说明】
- logic_expression（逻辑表达）：回答条理性、语言组织能力
- technical_depth（技术深度）：专业知识储备、技术理解程度
- stability（稳定性）：回答是否从容、有无紧张或卡顿
- solution_ability（方案能力）：问题分析和解决方案设计能力
- stress_resistance（抗压能力）：面对困难问题的表现
- communication（沟通技巧）：理解问题准确性、表达清晰度

【评分标准】
0-59分：表现很差，不合格，无法胜任该岗位
60-69分：表现欠佳，勉强及格，需要大幅提升
70-79分：表现一般，基本符合要求，有提升空间
80-89分：表现良好，达到预期，部分方面优秀
90-100分：表现卓越，显著超出预期，综合素质优秀

【评分强制要求】
1. 六个维度分数必须各不相同
2. 最高分和最低分之间的差距必须≥15分
3. 分数必须真实反映对话中展现的能力差异
4. 如果候选人回答混乱、答非所问、技术基础薄弱，技术深度和逻辑表达分数应低于50
5. 如果候选人态度不认真、敷衍回答，沟通技巧和稳定性分数应低于55
6. 如果候选人无法回答核心问题，方案能力分数应低于50
7. 整体分数应与维度分数的平均值一致，不得随意拉高"""

        return prompt
    
    def _parse_analysis_result(self, response: str) -> Dict[str, Any]:
        """解析LLM返回的分析结果"""
        try:
            # 尝试直接解析JSON
            # 移除可能的markdown代码块标记
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            
            # 验证必要字段
            if "strengths" not in result:
                result["strengths"] = ["表现良好"]
            if "weaknesses" not in result:
                result["weaknesses"] = ["尚有提升空间"]
            if "suggestions" not in result:
                result["suggestions"] = ["继续加强练习"]
            if "detailed_feedback" not in result:
                result["detailed_feedback"] = "面试表现正常，继续努力。"
            if "dimension_scores" not in result:
                # 如果没有维度分数，使用LLM给出的总分或默认70
                default_score = result.get("score", 70)
                result["dimension_scores"] = {
                    "logic_expression": default_score,
                    "technical_depth": default_score,
                    "stability": default_score,
                    "solution_ability": default_score,
                    "stress_resistance": default_score,
                    "communication": default_score
                }
            
            # 根据6个维度分数计算总分（取平均值）
            dimension_scores = result["dimension_scores"]
            expected_dimensions = [
                "logic_expression", "technical_depth", "stability",
                "solution_ability", "stress_resistance", "communication"
            ]
            
            # 收集所有有效的维度分数
            valid_scores = []
            for dim in expected_dimensions:
                if dim in dimension_scores and isinstance(dimension_scores[dim], (int, float)):
                    valid_scores.append(dimension_scores[dim])
            
            # 如果有维度分数，计算平均值作为总分
            if valid_scores:
                calculated_score = round(sum(valid_scores) / len(valid_scores))
                result["score"] = calculated_score
                logger.info(f"Calculated total score from dimensions: {valid_scores} -> {calculated_score}")
            elif "score" not in result:
                result["score"] = 70  # 默认分数
            
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            # 返回基于原始响应的结果
            return {
                "score": 70,
                "strengths": ["完成了面试对话"],
                "weaknesses": ["分析解析失败"],
                "suggestions": ["建议重新进行面试"],
                "detailed_feedback": response[:500] if response else "分析结果解析失败",
                "dimension_scores": {
                    "expression": 70,
                    "technical_depth": 70,
                    "logic": 70,
                    "communication": 70
                }
            }
    
    def _get_fallback_result(self, error_msg: str) -> Dict[str, Any]:
        """返回失败时的默认结果"""
        return {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["建议重新进行面试"],
            "detailed_feedback": f"分析失败：{error_msg}",
            "dimension_scores": {
                "expression": 0,
                "technical_depth": 0,
                "logic": 0,
                "communication": 0
            },
            "error": True
        }


# 单例实例
interview_analysis_service = InterviewAnalysisService()
