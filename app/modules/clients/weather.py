import httpx
from typing import Optional, Dict
from app.models.weather import WeatherForecast
from app.models.templates.weather_context_template import WeatherContextTemplate


class WeatherAPI:
    BASE_URL = "https://api.open-meteo.com/v1"
    
    @classmethod
    async def get_forecast(
        cls,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{cls.BASE_URL}/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "start_date": start_date,
                        "end_date": end_date,
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                        "timezone": "auto"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                forecast = WeatherForecast.from_api_response(
                    data, latitude, longitude, start_date, end_date
                )
                return forecast.model_dump() if forecast else None
                
        except Exception as e:
        
            print(f"Error fetching weather data: {str(e)}")
            return None
    
    @staticmethod
    def format(weather_data: Dict) -> str:    
        return WeatherContextTemplate.format(weather_data)
    
