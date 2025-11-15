import json
import asyncio
from typing import Dict, List, Optional, Any

from app.modules.tools.registry import ToolRegistry
from app.modules.clients.ollama import OllamaClient


class FunctionCaller:    
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_NUM_PREDICT = 50
    
    def __init__(self, tool_registry: ToolRegistry, llm_client: OllamaClient):
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self._cached_tool_schemas: Optional[List[Dict]] = None
    
    def get_tool_schemas(self) -> List[Dict]:
        if self._cached_tool_schemas is None:
            self._cached_tool_schemas = self.tool_registry.get_tool_schemas()
        return self._cached_tool_schemas
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        response = await self._call_llm(messages, temperature)
        tool_calls = self._extract_tool_calls(response)
        
        if not tool_calls:
            return self._build_response(response, [], tool_calls)
        
        tool_results = await self._execute_tools(tool_calls)
        return self._build_response(response, tool_results, tool_calls)
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float]
    ) -> Dict[str, Any]:
        tools = self.get_tool_schemas()
        return await self.llm_client.chat(
            messages=messages,
            temperature=temperature or self.DEFAULT_TEMPERATURE,
            tools=tools if tools else None,
            num_predict=self.DEFAULT_NUM_PREDICT
        )
    
    def _extract_tool_calls(self, response: Dict[str, Any]) -> Optional[List[Dict]]:
        tool_calls = response.get("tool_calls")
        if tool_calls:
            return tool_calls
        
        message = response.get("message", {})
        if isinstance(message, dict):
            tool_calls = message.get("tool_calls")
            if tool_calls:
                return tool_calls
        
        if "tool_calls" in response:
            return response["tool_calls"]
        
        return None
    
    async def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        tasks = [
            self._execute_single_tool(tool_call)
            for tool_call in tool_calls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            result for result in results
            if result and not isinstance(result, Exception)
        ]
    
    async def _execute_single_tool(self, tool_call: Dict) -> Optional[Dict]:
        function_name = tool_call.get("function", {}).get("name")
        function_args = self._parse_function_args(tool_call)
        
        if not function_name or not function_args:
            return None
        
        try:
            result = await self.tool_registry.call_tool(function_name, function_args)
            if result:
                return {
                    "tool_message": self._build_tool_message(function_name, result),
                    "tool_data": result
                }
        except Exception:
            pass
        
        return None
    
    def _parse_function_args(self, tool_call: Dict) -> Optional[Dict[str, Any]]:
        function_args = tool_call.get("function", {}).get("arguments", {})
        
        if isinstance(function_args, dict):
            return function_args
        
        if isinstance(function_args, str):
            try:
                return json.loads(function_args)
            except json.JSONDecodeError:
                return None
        
        return None
    
    def _build_tool_message(self, function_name: str, result: Dict) -> Dict:
        return {
            "role": "tool",
            "name": function_name,
            "content": json.dumps(result)
        }
    
    def _build_response(
        self,
        response: Dict[str, Any],
        tool_results: List[Dict],
        tool_calls: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        all_tool_data = [result["tool_data"] for result in tool_results] if tool_results else []
        
        return {
            "content": response.get("content", ""),
            "tool_data": all_tool_data[0] if all_tool_data else None,
            "all_tool_data": all_tool_data,
            "tool_calls": tool_calls
        }
    
    def format_tool_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        if not result:
            return f"Tool {tool_name} returned no data."
        
        tool_type = result.get("type")
        data = result.get("data", {})
        
        formatters = {
            "weather": lambda: f"Weather data for {data.get('location', 'location')}: {json.dumps(data, indent=2)}",
            "country": lambda: f"Country information: {json.dumps(data, indent=2)}",
            "visa": lambda: f"Visa information: {json.dumps(data, indent=2)}"
        }
        
        formatter = formatters.get(tool_type)
        return formatter() if formatter else json.dumps(result, indent=2)

