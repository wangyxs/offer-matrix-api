import json
from app.services.llm_service import llm_service
from app.schemas.interview import ChatRequest, ChatResponse
from sqlalchemy.orm import Session
from app.services.role_service import get_role_by_name
from app.services.rag_service import rag_service

class InterviewService:
    
    def process_chat(self, request: ChatRequest, db: Session) -> ChatResponse:
        """
        Main orchestration logic.
        """
        # 0. RAG Retrieval
        rag_context = ""
        role = get_role_by_name(db, request.target_position)
        if role:
            # Query RAG with user input or current question to get relevant docs
            query = f"{request.target_position} {request.current_question or ''} {request.user_input}"
            rag_context = rag_service.search_context(query, role.id)
            if rag_context:
                rag_context = f"\nRelevant Context (Resume/Materials):\n{rag_context}\n"

        # 1. Identify Intent
        intent_data = self._identify_intent(request.user_input, request.current_question, request.target_position, request.history)
        intention = intent_data.get("intention_type", "consult")
        
        # 2. Logic Dispatch
        if intention == "evaluate" or intention == "get_evaluation": 
             if not request.current_question:
                 return self._generate_question(request.target_position, "我想开始面试", request.history, rag_context)
             
             evaluation = self._evaluate_answer(request.target_position, request.current_question, request.user_input, rag_context)
             return ChatResponse(reply=evaluation, action="listen")
             
        elif intention == "ask_question" or intention == "start_interview": 
            question = self._generate_question(request.target_position, request.user_input, request.history, rag_context)
            return ChatResponse(reply=question, action="listen")
            
        elif intention == "clarify" or intention == "follow_up":
             clarification = self._clarify_question(request.target_position, request.current_question, request.user_input, rag_context)
             return ChatResponse(reply=clarification, action="listen")
             
        else: 
            response = self._default_chat(request.user_input, request.history, rag_context)
            return ChatResponse(reply=response, action="listen")

    def _format_history(self, history: list) -> str:
        if not history:
            return "No history."
        return "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in history[-10:]]) # Limit context

    def _identify_intent(self, user_input: str, current_question: str, position: str, history: list) -> dict:
        history_str = self._format_history(history)
        system_prompt = f"""
Current Question: {current_question if current_question else 'None'}
User Input: {user_input}
Conversation History:
{history_str}

# Task: Extract intent from user input and history, return JSON.
expected_position: The job position user wants (e.g., {position} if implied).
intention_type: One of ['ask_question', 'get_evaluation', 'consult', 'follow_up'].

# Rules:
- If history shows user just answered a question -> 'get_evaluation'
- If user says 'Next' or 'Ready' -> 'ask_question'
- If history is empty and user says 'Start' -> 'ask_question'
- If input is an answer to the Current Question -> 'get_evaluation'
"""
        messages = [
            {"role": "system", "content": "You are an intent classifier. Return ONLY JSON."},
            {"role": "user", "content": system_prompt}
        ]
        
        try:
            response = llm_service.chat_completion(messages, temperature=0.1)
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except:
            return {"intention_type": "consult", "expected_position": position}

    def _evaluate_answer(self, position: str, question: str, answer: str, context: str = "") -> str:
        system_prompt = f"""
Target Position: {position}
Interview Question: {question}
Candidate Answer: {answer}
{context}

## Role: Evaluator.
## Output: Score (0-100), key points, pros/cons.
## If context is provided, verify if the answer aligns with the resume/materials.
## END with: "Ready for the next question?"
"""
        messages = [{"role": "user", "content": system_prompt}]
        return llm_service.chat_completion(messages)

    def _generate_question(self, position: str, user_request: str, history: list, context: str = "") -> str:
        history_str = self._format_history(history)
        system_prompt = f"""
Target Position: {position}
User Request: {user_request}
History:
{history_str}
{context}

## Role: Interviewer.
## Task: Generate the NEXT interview question.
## Rules:
1. Do NOT repeat questions found in History.
2. If History is empty, start with a basic question (Intro/Background).
3. If context (Resume) is available, ask specific questions about their skills/projects.
4. Output ONLY the question.
"""
        messages = [{"role": "user", "content": system_prompt}]
        return llm_service.chat_completion(messages)

    def _clarify_question(self, position: str, question: str, user_query: str, context: str = "") -> str:
        system_prompt = f"""
Target Position: {position}
Current Question: {question}
User Query: {user_query}
{context}
## Role: Interviewer. Clarify doubts.
"""
        messages = [{"role": "user", "content": system_prompt}]
        return llm_service.chat_completion(messages)

    def _default_chat(self, user_input: str, history: list, context: str = "") -> str:
        history_str = self._format_history(history)
        system_prompt = f"""
User Input: {user_input}
History:
{history_str}
{context}
## Role: Career Expert.
## Goal: Answer briefly, then guide user back to "Simulate Interview".
"""
        messages = [{"role": "user", "content": system_prompt}]
        return llm_service.chat_completion(messages)

ai_interview_service = InterviewService()
