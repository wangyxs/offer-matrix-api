from zhipuai import ZhipuAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.ZHIPUAI_API_KEY)
        self.model = settings.AI_MODEL

    def chat_completion(self, messages: list[dict], temperature: float = 0.7) -> str:
        """
        Call ZhipuAI GLM-4 model for chat completion.
        :param messages: List of message dicts [{'role': 'user', 'content': '...'}, ...]
        :param temperature: Creativity parameter
        :return: Content of the AI response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Sorry, I am having trouble connecting to the AI service right now."

llm_service = LLMService()
