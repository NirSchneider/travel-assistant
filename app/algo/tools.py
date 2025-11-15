from typing import Optional, Dict

from app.modules.clients.weather import WeatherAPI
from app.modules.clients.country import CountryAPI
from app.modules.clients.visa import VisaAPI
from app.modules.clients.geocoding import GeocodingClient


async def fetch_weather_for_location(
    location: str,
    start_date: str,
    end_date: str
) -> Optional[Dict]:
    coords = await GeocodingClient.get_coordinates(location)
    if not coords:
        return None
    
    lat, lon = coords.latitude, coords.longitude
    weather_data = await WeatherAPI.get_forecast(lat, lon, start_date, end_date)
    
    if weather_data:
        weather_data["location"] = location
    
    return weather_data


async def fetch_country_info(country_name: str) -> Optional[Dict]:
    
    return await CountryAPI.get_country_info(country_name)


async def fetch_visa_info(
    origin_country: str,
    destination_country: str
) -> Optional[Dict]:
    return await VisaAPI.get_visa_info(origin_country, destination_country)
