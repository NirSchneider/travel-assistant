import json
import re

from app.modules.clients.ollama import OllamaClient
from app.prompts.builder.prompts import render_template
from app.consts.roles import MessageRole
from app.consts.intents import LEGITIMATE_INTENT, VALID_INTENTS, NON_VALID_INTENT


class IntentExtractor:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    def _parse_response(self, response: str) -> str:
        response = response.strip()
        
        json_match = re.search(r'\{[^{}]*"intent"\s*:\s*"[^"]*"[^{}]*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            data = json.loads(response)
            intent = data.get("intent", "").strip().lower()
            
            all_intents = VALID_INTENTS + NON_VALID_INTENT
            if intent not in all_intents:
                return LEGITIMATE_INTENT
            
            return intent
        except json.JSONDecodeError:
            return LEGITIMATE_INTENT
    
    async def extract(self, message: str) -> str:
        prompt = render_template("intent_extraction.j2", message=message)

        messages = [
            {
                "role": MessageRole.USER.value,
                "content": prompt
            }
        ]
        
        try:
            response = await self.llm.chat(messages, temperature=0.0, num_predict=30)
            content = response.get("content", "") if isinstance(response, dict) else response
            return self._parse_response(content)
            
        except Exception as e:
            print(f"Intent extraction error: {str(e)}")
            return LEGITIMATE_INTENT

