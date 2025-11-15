import json
import re
import httpx
from typing import Optional, Dict
from app.consts.models import QWEN_MODEL
from app.modules.clients.ollama import OllamaClient
from app.prompts.builder.prompts import render_template
from app.models.templates.visa_context_template import VisaContextTemplate
from app.consts.visa import (
    VISA_API_BASE_URL,
    VISA_API_TIMEOUT,
    REST_COUNTRIES_TIMEOUT,
    REST_COUNTRIES_BASE_URL,
    COUNTRY_NAME_TO_CODE,
    VISA_CATEGORY_TO_STATUS,
    VISA_STATUS_DESCRIPTIONS,
    VISA_TEXT_KEYWORDS,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_SOURCE,
    MAX_TEXT_EXTRACT_LENGTH
)


class VisaAPI:
    @staticmethod
    async def get_visa_info(
        origin_country: str,
        destination_country: str
    ) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=VISA_API_TIMEOUT) as client:
                response = await VisaAPI._fetch_visa_data_free_api(
                    client, origin_country, destination_country
                )
                if response:
                    return VisaAPI._parse_visa_data(response, origin_country, destination_country)
            
            result = await VisaAPI._fetch_visa_data_llm(origin_country, destination_country)
            return result
                
        except Exception as e:
            print(f"Error fetching visa data: {str(e)}")
            return None
    
    @staticmethod
    async def _fetch_visa_data_llm(
        origin: str,
        destination: str
    ) -> Optional[Dict]:
        try:
            llm = OllamaClient(model=QWEN_MODEL)
            
            prompt = render_template("visa_llm_prompt.j2", origin=origin, destination=destination)
            messages = [{"role": "user", "content": prompt}]
            response = await llm.chat(messages, temperature=DEFAULT_LLM_TEMPERATURE)
            
            content = response.get("content", "").strip()
            content = VisaAPI._extract_json_from_content(content)
            
            try:
                visa_data = json.loads(content)
                return {
                    "origin": origin,
                    "destination": destination,
                    "visa_required": visa_data.get("visa_required", "unknown"),
                    "visa_type": visa_data.get("visa_type"),
                    "stay_duration": visa_data.get("stay_duration"),
                    "notes": visa_data.get("notes", ""),
                    "source": DEFAULT_SOURCE
                }
            except json.JSONDecodeError:
                return VisaAPI._parse_visa_from_text(content, origin, destination)
                
        except Exception as e:
            print(f"Error fetching visa data from LLM: {str(e)}")
            return None

    @staticmethod
    def _extract_json_from_content(content: str) -> str:
        json_match = re.search(r'\{[^{}]*"visa_required"[^{}]*\}', content, re.DOTALL)
        return json_match.group(0) if json_match else content
    
    @staticmethod
    def _parse_visa_from_text(text: str, origin: str, destination: str) -> Dict:
        text_lower = text.lower()
        visa_required = "unknown"
        
        for status, keywords in VISA_TEXT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                visa_required = status
                break
        
        return {
            "origin": origin,
            "destination": destination,
            "visa_required": visa_required,
            "visa_type": None,
            "stay_duration": None,
            "notes": text[:MAX_TEXT_EXTRACT_LENGTH] if text else "Visa information from LLM",
            "source": DEFAULT_SOURCE
        }
    
    @staticmethod
    async def _fetch_visa_data_free_api(
        client: httpx.AsyncClient,
        origin: str,
        destination: str
    ) -> Optional[Dict]:
        try:
            origin_code = await VisaAPI._country_name_to_code(origin)
            destination_code = await VisaAPI._country_name_to_code(destination)
            
            if not origin_code or not destination_code:
                print(f"Could not convert country names to codes: {origin} -> {origin_code}, {destination} -> {destination_code}")
                return None
            
            response = await client.get(
                f"{VISA_API_BASE_URL}/visa/{origin_code}/{destination_code}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling free visa API: {str(e)}")
            return None
    
    @staticmethod
    async def _country_name_to_code(country_name: str) -> Optional[str]:
        country_lower = country_name.strip().lower()
        
        if country_lower in COUNTRY_NAME_TO_CODE:
            return COUNTRY_NAME_TO_CODE[country_lower]
        
        try:
            async with httpx.AsyncClient(timeout=REST_COUNTRIES_TIMEOUT) as client:
                response = await client.get(
                    f"{REST_COUNTRIES_BASE_URL}/name/{country_name}",
                    params={"fullText": "false"}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        country_code = data[0].get("cca2", "").upper()
                        if country_code:
                            return country_code
        except Exception:
            pass
        
        return None
    
    
    @staticmethod
    def _parse_visa_data(
        api_response: Dict,
        origin: str,
        destination: str
    ) -> Dict:
        category = api_response.get("category", {})
        category_code = category.get("code", "") if isinstance(category, dict) else ""
        category_name = category.get("name", "") if isinstance(category, dict) else ""
        duration = api_response.get("dur")
        
        visa_required = VISA_CATEGORY_TO_STATUS.get(category_code, "unknown")
        stay_duration = f"{duration} days" if duration else None
        notes = VisaAPI._build_notes(category_name, duration)
        status_description = VisaAPI._format_visa_status(visa_required, None)
        
        return {
            "origin_country": origin,
            "destination_country": destination,
            "visa_required": visa_required,
            "visa_type": None,
            "status_description": status_description,
            "stay_duration": stay_duration,
            "notes": notes,
            "evisa_link": None,
            "raw_data": api_response
        }

    @staticmethod
    def _build_notes(category_name: str, duration: Optional[int]) -> str:
        notes = category_name if category_name else ""
        if duration:
            if notes:
                notes += f" for up to {duration} days"
            else:
                notes = f"Up to {duration} days"
        return notes
    
    @staticmethod
    def _format_visa_status(visa_required: str, visa_type: Optional[str]) -> str:
        base_status = VISA_STATUS_DESCRIPTIONS.get(
            visa_required.lower(),
            "Visa requirement information not available"
        )
        
        if visa_type:
            return f"{base_status} ({visa_type})"
        
        return base_status
    
    @staticmethod
    def format(visa_data: Dict) -> str:
        return VisaContextTemplate.format(visa_data)

