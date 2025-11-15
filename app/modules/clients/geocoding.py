import httpx
from typing import NamedTuple, Optional


class Coordinates(NamedTuple):
    latitude: float
    longitude: float


class GeocodingClient:    
    BASE_URL = "https://geocoding-api.open-meteo.com/v1"
    REQUEST_TIMEOUT = 10.0
    MAX_RESULTS = 1
    
    @classmethod
    async def get_coordinates(cls, location: str) -> Optional[Coordinates]:
        if not location or not location.strip():
            return None
        
        try:
            async with httpx.AsyncClient(timeout=cls.REQUEST_TIMEOUT) as client:
                response = await client.get(
                    f"{cls.BASE_URL}/search",
                    params={"name": location.strip(), "count": cls.MAX_RESULTS}
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    return None
                
                first_result = results[0]
                latitude = first_result.get("latitude")
                longitude = first_result.get("longitude")
                
                if latitude is None or longitude is None:
                    return None
                
                return Coordinates(latitude=latitude, longitude=longitude)
                
        except Exception as e:
            print(f"Error getting coordinates for '{location}': {str(e)}")
            return None

