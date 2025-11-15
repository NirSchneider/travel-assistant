import json
import re
from typing import Optional

from app.modules.clients.ollama import OllamaClient
from app.prompts.builder.prompts import render_template


class LocationExtractor:    
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    def _parse_response(self, response: str) -> Optional[str]:
        response = response.strip()
        
        json_match = re.search(r'\{[^{}]*"location"\s*:\s*"[^"]*"[^{}]*"is_fictional"\s*:\s*(true|false)[^{}]*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            data = json.loads(response)
            location = data.get("location", "").strip()
            is_fictional = data.get("is_fictional", False)
            
            if location.upper() in ["NONE", "NO LOCATION", "N/A", ""]:
                return None
            
            if is_fictional:
                return 'fictional'
            
            return location.lower()
        except json.JSONDecodeError:
            json_match = re.search(r'\{[^{}]*"location"\s*:\s*"[^"]*"[^{}]*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
                try:
                    data = json.loads(response)
                    location = data.get("location", "").strip()
                    if location.upper() in ["NONE", "NO LOCATION", "N/A", ""]:
                        return None
                    if location.lower() == "fictional":
                        return None
                    return location.lower()
                except json.JSONDecodeError:
                    pass
            
            if response.upper() in ["NONE", "NO LOCATION", "N/A", ""]:
                return None
            return response.lower()
    
    async def extract(self, message: str) -> Optional[str]:
        prompt = render_template("location_extraction.j2", message=message)

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
            print(f"Location extraction error: {str(e)}")
            return None

