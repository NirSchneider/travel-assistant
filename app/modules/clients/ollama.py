from typing import List, Dict, Optional, Any
import ollama
from app.consts.models import LLAMA_MODEL


class OllamaClient:
    def __init__(self, model: str = LLAMA_MODEL):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.temperature = 0.0
        self.provider = "ollama"

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        tools: Optional[List[Dict]] = None,
        num_predict: Optional[int] = None,
    ) -> Dict:
        try:
            client = ollama.AsyncClient(host=self.base_url)
            
            options = {"temperature": temperature or self.temperature}
            if num_predict is not None:
                options["num_predict"] = num_predict
            
            chat_params = {
                "model": self.model,
                "messages": messages,
                "options": options
            }
            if tools:
                chat_params["tools"] = tools
            
            response = await client.chat(**chat_params)
            message = self._extract_message(response)
            
            return {
                "content": self._extract_content(message),
                "tool_calls": self._extract_tool_calls(message)
            }

        except Exception as e:
            raise RuntimeError(f"Error calling Ollama client: {str(e)}")

    def _extract_message(self, response: Any) -> Any:
        if hasattr(response, 'message'):
            return response.message
        return response.get("message", {})

    def _extract_content(self, message: Any) -> str:
        if hasattr(message, 'content'):
            return (message.content or "").strip()
        if isinstance(message, dict):
            return message.get("content", "").strip()
        return ""

    def _extract_tool_calls(self, message: Any) -> Optional[List[Dict]]:
        if hasattr(message, 'tool_calls') and message.tool_calls:
            return [self._convert_tool_call(tc) for tc in message.tool_calls]
        
        if isinstance(message, dict):
            return message.get("tool_calls")
        
        return None

    def _convert_tool_call(self, tool_call: Any) -> Dict:
        if not hasattr(tool_call, 'function'):
            return {}
        
        func = tool_call.function
        return {
            "id": getattr(tool_call, 'id', None),
            "type": "function",
            "function": {
                "name": func.name if hasattr(func, 'name') else getattr(func, 'name', ''),
                "arguments": func.arguments if hasattr(func, 'arguments') else getattr(func, 'arguments', {})
            }
        }
