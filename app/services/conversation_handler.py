from typing import List, Dict, Optional

from app.modules.clients.ollama import OllamaClient
from app.modules.extractor.manager import ExtractorManager
from app.models.extraction_result import ExtractionResult
from app.modules.response_generator import ResponseGenerator
from app.modules.agents.research_agent import ResearchAgent
from app.modules.tools.registry import ToolRegistry
from app.prompts import build_system_message
from app.consts.roles import MessageRole
from app.consts.intents import NON_LEGIT_INTENT, NON_VALID_INTENT, NON_VALID_INTENT_MESSAGES


class ConversationHandler:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
        self.messages: List[Dict[str, str]] = []
        
    def start_conversation(self):
        system_prompt = build_system_message()
        self.messages = [system_prompt]
    
    async def handle(self, user_message: str) -> str:
        self.add_message(user_message, MessageRole.USER)
        
        extractor = ExtractorManager(self.llm)
        extractions = await extractor.extract(user_message)
        
        if extractions.intent in NON_VALID_INTENT:
            message = NON_VALID_INTENT_MESSAGES.get(extractions.intent, NON_VALID_INTENT_MESSAGES[NON_LEGIT_INTENT])
            return message
        
        await self._fetch_external_data(extractions)
        
        response_generator = ResponseGenerator(self.llm, self.messages, extractions)
        assistant_response = await response_generator.generate_response()
        
        self.add_message(assistant_response, MessageRole.ASSISTANT)
        
        return assistant_response
    
    def add_message(self, content: str, role: MessageRole, position: Optional[int] = None):
        message = {
            "role": role,
            "content": content
        }
        if position is not None:
            self.messages.insert(position, message)
        else:
            self.messages.append(message)
            
    async def _fetch_external_data(self, extracted_info: ExtractionResult):
        self.research_agent = ResearchAgent(self.llm, ToolRegistry())
        external_data = await self.research_agent.research(extracted_info, self.messages)
        
        if external_data:
            self._inject_system_message(external_data)
    
    def _inject_system_message(self, external_data: List[Dict]):
        external_data_content = "\n".join([data['data'] for data in external_data])
        self.add_message(external_data_content, MessageRole.SYSTEM, position=-1)
