import json
import re
from typing import Optional

from app.modules.clients.ollama import OllamaClient
from app.prompts.builder.prompts import render_template


class DateExtractor:    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    def _parse_response(self, response: str) -> Optional[str]:
        response = response.strip()
        
        json_match = re.search(r'\{[^{}]*"date"\s*:\s*"[^"]*"[^{}]*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            data = json.loads(response)
            date = data.get("date", "").strip()
            
            if date.upper() in ["NONE", "NO DATE", "N/A", ""]:
                return None
            
            return date.lower()
        except json.JSONDecodeError:
            if response.upper() in ["NONE", "NO DATE", "N/A", ""]:
                return None
            return response.lower()
    
    async def extract(self, message: str) -> Optional[str]:
        prompt = render_template("date_extraction.j2", message=message)

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = await self.llm.chat(messages, temperature=0.0, num_predict=30)
            content = response.get("content", "") if isinstance(response, dict) else response
            return self._parse_response(content)
            
        except Exception as e:
            print(f"Date extraction error: {str(e)}")
            return None

