from typing import List, Dict, Optional

from app.algo.processor.user_violation import UserViolationProcessor
from app.models.extraction_result import ExtractionResult
from app.modules.clients.ollama import OllamaClient
from app.algo.processor.response import LLMResponseGenerator
from app.prompts.builder.prompts import render_template
from app.consts.roles import MessageRole
from app.consts.intents import VALID_INTENTS
from app.consts.context import MAX_CONTEXT_MESSAGES


class ResponseGenerator:
    def __init__(self, llm_client: OllamaClient, messages: List[Dict[str, str]], extraction_result: ExtractionResult):
        self.llm_client = llm_client
        self.messages = messages
        self.extraction_result = extraction_result
    
    async def generate_response(self) -> str:
        user_violation_response = await self._check_user_violation()
        if user_violation_response:
            return user_violation_response
        
        formatted_messages = self._format_messages_pipeline()
        
        response_processor = LLMResponseGenerator(self.llm_client)
        return await response_processor.generate(formatted_messages)
    
    async def _check_user_violation(self) -> Optional[str]:
        location = self.extraction_result.location
        
        if location == 'fictional':
            violation_processor = UserViolationProcessor(self.llm_client)
            violation_feedback = await violation_processor.generate_response(self.messages[-1].get('content', ''))
            self.messages.append({
                "role": MessageRole.ASSISTANT.value,
                "content": violation_feedback
            })
            return violation_feedback
        
        return None
    
    def _format_messages_pipeline(self) -> List[Dict[str, str]]:
        formatted = self.messages.copy()
        
        formatted = self._inject_system_message(formatted)
        
        formatted = self._handle_context_window(formatted)
        
        return formatted
    
    def _inject_system_message(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not self.extraction_result.intent:
            return messages

        if self.extraction_result.intent in VALID_INTENTS[:-2]:
            system_message_content = render_template("response_generator.j2", intent=self.extraction_result.intent)
            system_message = {
                "role": MessageRole.SYSTEM.value,
                "content": system_message_content
            }
            messages.insert(-1, system_message)
        
        return messages
    
    def _handle_context_window(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        total_count = len(messages)
        
        if total_count <= MAX_CONTEXT_MESSAGES:
            return messages
        
        partitioned = self._partition_by_role(messages)
        system_context = partitioned['system']
        conversation_messages = partitioned['conversation']
        
        system_count = len(system_context)
        available_slots = MAX_CONTEXT_MESSAGES - system_count
        
        if available_slots > 0:
            trimmed_conversation = conversation_messages[-available_slots:]
            return system_context + trimmed_conversation
        
        primary_system = system_context[0] if system_context else None
        recent_conversation = conversation_messages[-(MAX_CONTEXT_MESSAGES - 1):]
        
        if primary_system:
            return [primary_system] + recent_conversation
        
        return recent_conversation[-MAX_CONTEXT_MESSAGES:]
    
    def _partition_by_role(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, List[Dict[str, str]]]:
        system = []
        conversation = []
        
        for msg in messages:
            role = msg.get('role', '')
            if role == MessageRole.SYSTEM.value:
                system.append(msg)
            else:
                conversation.append(msg)
        
        return {'system': system, 'conversation': conversation}
    

