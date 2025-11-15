from app.modules.clients.ollama import OllamaClient
from app.prompts.builder.prompts import render_template
from app.consts.roles import MessageRole


class UserViolationProcessor:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    async def generate_response(self, message: str) -> str:
        prompt = render_template("user_violation.j2", message=message)
        
        messages = [
            {
                "role": MessageRole.USER.value,
                "content": prompt
            }
        ]
        
        try:
            response = await self.llm.chat(messages, temperature=0.5, num_predict=100)
            content = response.get("content", "") if isinstance(response, dict) else response
            return content.strip()
        except Exception as e:
            print(f"User violation processor error: {str(e)}")
            return "I'd love to help, but I need a real destination on Earth! Could you tell me about an actual place you'd like to visit?"