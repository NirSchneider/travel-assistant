import httpx
from typing import Optional, Dict
from app.models.templates.country_context_template import CountryContextTemplate
from app.modules.clients.geocoding import GeocodingClient


class CountryAPI:
    BASE_URL = "https://restcountries.com/v3.1"
    
    @staticmethod
    async def get_country_info(location: str) -> Optional[Dict]:
        country_data = await CountryAPI._try_get_country(location)
        if country_data:
            return country_data
        
        country_name = await CountryAPI._resolve_country_from_location(location)
        if country_name:
            country_data = await CountryAPI._try_get_country(country_name)
            return country_data
        
        return None
    
    @staticmethod
    async def _try_get_country(country_name: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{CountryAPI.BASE_URL}/name/{country_name}",
                    params={"fullText": "false"}
                )
                response.raise_for_status()
                data = response.json()
                
                if not data or len(data) == 0:
                    return None
                
                country = data[0]
                
                return CountryAPI._parse_country_data(country)
                
        except Exception as e:
            print(f"Error fetching country data for '{country_name}': {str(e)}")
            return None
    
    @staticmethod
    async def _resolve_country_from_location(location: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{GeocodingClient.BASE_URL}/search",
                    params={"name": location.strip(), "count": 1}
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return None
                
                first_result = results[0]
                country = first_result.get("country")
                
                return country
                
        except Exception as e:
            print(f"Error resolving country from location '{location}': {str(e)}")
            return None
    
    @staticmethod
    def _parse_country_data(country: dict) -> Dict:
        name = country.get("name", {}).get("common", "Unknown")
        capital = country.get("capital", ["Unknown"])[0] if country.get("capital") else "Unknown"
        region = country.get("region", "Unknown")
        subregion = country.get("subregion", "")
        
        currencies = country.get("currencies", {})
        currency = list(currencies.values())[0].get("name", "Unknown") if currencies else "Unknown"
        currency_code = list(currencies.keys())[0] if currencies else "Unknown"
        
        languages = country.get("languages", {})
        language_list = list(languages.values()) if languages else ["Unknown"]
        
        timezones = country.get("timezones", ["Unknown"])
        
        return {
            "name": name,
            "capital": capital,
            "region": f"{region}, {subregion}" if subregion else region,
            "currency": f"{currency} ({currency_code})",
            "languages": language_list,
            "timezone": timezones[0] if timezones else "Unknown",
            "raw_data": country
        }
    
    @staticmethod
    def format(country_data: Dict) -> str:
        return CountryContextTemplate.format(country_data)

