from typing import List, Dict, Optional
from datetime import datetime, timedelta

from app.consts.models import QWEN_MODEL
from app.modules.clients.ollama import OllamaClient
from app.modules.tools.function_caller import FunctionCaller
from app.modules.tools.registry import ToolRegistry
from app.models.extraction_result import ExtractionResult
from app.modules.clients.weather import WeatherAPI
from app.modules.clients.country import CountryAPI
from app.modules.clients.visa import VisaAPI
from app.consts.roles import MessageRole
from app.prompts.builder.prompts import render_template
from app.algo.tools import fetch_visa_info, fetch_weather_for_location, fetch_country_info
from app.algo.extractor.visa_country import VisaCountryExtractor
from app.consts.intents import PACKING_INTENT, DESTINATION_INTENT, ATTRACTIONS_INTENT


class ResearchAgent:
    def __init__(self, llm_client: OllamaClient, tool_registry: ToolRegistry):
       
        self.llm = OllamaClient(model=QWEN_MODEL)
        self.tool_registry = tool_registry
        self.function_caller = FunctionCaller(tool_registry, self.llm)
    
    async def research(
        self,
        extraction_result: ExtractionResult,
        conversation_messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        if not extraction_result.intent:
            return []
        
        last_user_message = self._get_last_user_message(conversation_messages)
        is_visa_query = self._is_visa_query(last_user_message)
        
        if not extraction_result.location and not is_visa_query:
            return []
        
        # OPTIMIZATION: For simple visa queries, skip LLM function calling and directly call the tool
        if is_visa_query:
            return await self._handle_visa_query_directly(last_user_message, extraction_result)
        
        research_prompt = self._build_research_prompt(extraction_result, conversation_messages)
        
        research_messages = [
            {
                "role": MessageRole.SYSTEM.value,
                "content": research_prompt
            }
        ]
        
        try:
            result = await self.function_caller.chat_with_tools(messages=research_messages)

            all_tool_data = result.get("all_tool_data", [])
            if not all_tool_data and result.get("tool_data"):
                all_tool_data = [result.get("tool_data")]
            
            external_data = []
            
            for tool_data in all_tool_data:
                if tool_data:
                    external_data.extend(self._format_tool_results(tool_data))
            
            return external_data
            
        except Exception as e:
            print(f"Research agent error: {str(e)}")
            return await self._fallback_research(extraction_result)
    

    async def _handle_visa_query_directly(
        self,
        user_message: str,
        extraction_result: ExtractionResult
    ) -> List[Dict[str, str]]:
        origin_country, destination_country = VisaCountryExtractor.extract_countries(user_message, extraction_result)
        
        if origin_country and destination_country:
            visa_data = await fetch_visa_info(origin_country, destination_country)
            if visa_data:
                return self._format_tool_results({
                    "type": "visa",
                    "data": visa_data
                })
        
        research_prompt = self._build_research_prompt(extraction_result, [
            {"role": MessageRole.USER.value, "content": user_message}
        ])
        research_messages = [{"role": MessageRole.SYSTEM.value, "content": research_prompt}]
        result = await self.function_caller.chat_with_tools(messages=research_messages)
        
        all_tool_data = result.get("all_tool_data", [])
        if not all_tool_data and result.get("tool_data"):
            all_tool_data = [result.get("tool_data")]
        
        external_data = []
        for tool_data in all_tool_data:
            if tool_data:
                external_data.extend(self._format_tool_results(tool_data))
        
        return external_data
    
    def _build_research_prompt(self, extraction_result: ExtractionResult, conversation_messages: List[Dict[str, str]]) -> str:
        last_user_message = self._get_last_user_message(conversation_messages)
        
        return render_template(
            "research_agent.j2",
            intent=extraction_result.intent,
            user_query=last_user_message,
            location=extraction_result.location,
            date=extraction_result.date
        )
    
    def _format_tool_results(self, tool_data: Optional[Dict]) -> List[Dict[str, str]]:
        if not tool_data:
            return []
        
        tool_type = tool_data.get("type")
        data = tool_data.get("data", {})
        
        formatted_data = []
        
        if tool_type == "weather" and data:
            formatted_weather = WeatherAPI.format(data)
            formatted_data.append({
                'type': 'weather',
                'data': formatted_weather
            })
        
        elif tool_type == "country" and data:
            formatted_country = CountryAPI.format(data)
            formatted_data.append({
                'type': 'country_info',
                'data': formatted_country
            })
        
        elif tool_type == "visa" and data:
            formatted_visa = VisaAPI.format(data)
            formatted_data.append({
                'type': 'visa_info',
                'data': formatted_visa
            })
        
        return formatted_data
    
    # Fallback research for when the LLM function calling fails
    # Results are faster but I wanted to present function calling capability
    async def _fallback_research(self, extraction_result: ExtractionResult) -> List[Dict[str, str]]:
        external_data = []
        
        if extraction_result.intent == PACKING_INTENT and extraction_result.location:
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            weather_data = await fetch_weather_for_location(
                extraction_result.location,
                start_date,
                end_date
            )
            if weather_data:
                formatted_weather = WeatherAPI.format(weather_data)
                external_data.append({
                    'type': 'weather',
                    'data': formatted_weather
                })
        
        elif extraction_result.intent in [DESTINATION_INTENT, ATTRACTIONS_INTENT] and extraction_result.location:
            country_data = await fetch_country_info(extraction_result.location)
            if country_data:
                formatted_country = CountryAPI.format(country_data)
                external_data.append({
                    'type': 'country_info',
                    'data': formatted_country
                })
        
        return external_data

    @staticmethod
    def _is_visa_query(message: str) -> bool:
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in [
            "visa", "passport", "entry requirement", "travel restriction"
        ])
    
    def _get_last_user_message(self, conversation_messages: List[Dict[str, str]]) -> str:
        for msg in reversed(conversation_messages):
            if msg.get("role") == MessageRole.USER.value:
                return msg.get("content", "")
        return ""

