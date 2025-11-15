from typing import List, Dict, Optional

from app.modules.clients.ollama import OllamaClient


class LLMResponseGenerator:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = 0.3
    ) -> str:
        try:
            response = await self.llm.chat(messages, temperature=temperature, num_predict=500)
            content = response.get("content", "") if isinstance(response, dict) else response
            return content
        except Exception as e:
            print(f"Response generation error: {str(e)}")
            return f"I encountered an error while processing your request. Please try again. (Error: {str(e)})"
