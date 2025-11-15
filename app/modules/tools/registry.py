from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.algo.tools import fetch_weather_for_location, fetch_country_info, fetch_visa_info


class ToolRegistry:    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_tools()
    
    def _register_tools(self):
        self.tools = {
            "fetch_weather": {
                "description": "Get weather forecast for a location and date range. Use this when the user asks about weather, packing suggestions, or needs climate information for a destination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city or location name (e.g., 'Paris', 'Tokyo', 'New York')"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format.",
                            "default": None
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format.",
                            "default": None
                        }
                    },
                    "required": ["location"]
                },
                "function": self._fetch_weather_wrapper
            },
            "fetch_country_info": {
                "description": "Get detailed information about a country including culture, currency, language, and travel tips. Use this when the user asks about destinations, attractions, or general country information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country_name": {
                            "type": "string",
                            "description": "The name of the country (e.g., 'France', 'Japan', 'Brazil')"
                        }
                    },
                    "required": ["country_name"]
                },
                "function": self._fetch_country_info_wrapper
            },
            "fetch_visa_info": {
                "description": "Get visa requirements and travel restrictions for traveling from one country to another. Use this when the user asks about visa requirements, passport requirements, entry requirements, or travel restrictions. Examples: 'Do I need a visa for Japan?', 'Does Israel need a passport for Japan?', 'What are the visa requirements for France?'",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_country": {
                            "type": "string",
                            "description": "The country of the traveler's passport/nationality (e.g., 'Israel', 'United States', 'United Kingdom')"
                        },
                        "destination_country": {
                            "type": "string",
                            "description": "The destination country the traveler wants to visit (e.g., 'Japan', 'France', 'Brazil')"
                        }
                    },
                    "required": ["origin_country", "destination_country"]
                },
                "function": self._fetch_visa_info_wrapper
            }
        }
    
    async def _fetch_weather_wrapper(self, location: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        result = await fetch_weather_for_location(location, start_date, end_date)
                
        return {
            "type": "weather",
            "data": result
        } if result else None
    
    async def _fetch_country_info_wrapper(self, country_name: str) -> Dict[str, Any]:
        result = await fetch_country_info(country_name)
        return {
            "type": "country",
            "data": result
        } if result else None
    
    async def _fetch_visa_info_wrapper(self, origin_country: str, destination_country: str) -> Dict[str, Any]:
        result = await fetch_visa_info(origin_country, destination_country)
        return {
            "type": "visa",
            "data": result
        } if result else None
    
    def get_tool_schemas(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool_name, tool in self.tools.items()
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        try:
            result = await tool["function"](**arguments)
            return result
        except Exception as e:
            print(f"Error calling tool {tool_name}: {str(e)}")
            return None

