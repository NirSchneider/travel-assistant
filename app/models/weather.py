from typing import Optional, Dict, List
from pydantic import BaseModel, computed_field
from statistics import mean


class DailyWeatherData(BaseModel):
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: List[float]
    weathercode: List[int]
    time: Optional[List[str]] = None
    
    @computed_field
    @property
    def avg_high(self) -> float:
        return mean(self.temperature_2m_max) if self.temperature_2m_max else 0.0
    
    @computed_field
    @property
    def avg_low(self) -> float:
        return mean(self.temperature_2m_min) if self.temperature_2m_min else 0.0
    
    @computed_field
    @property
    def total_precipitation(self) -> float:
        return sum(self.precipitation_sum) if self.precipitation_sum else 0.0


class WeatherForecast(BaseModel):
    latitude: float
    longitude: float
    start_date: str
    end_date: str
    daily: DailyWeatherData
    
    @computed_field
    @property
    def location(self) -> str:
        return f"{self.latitude:.2f}, {self.longitude:.2f}"
    
    @computed_field
    @property
    def temp_range(self) -> str:
        return f"{self.daily.avg_low:.0f}°C to {self.daily.avg_high:.0f}°C"
    
    @computed_field
    @property
    def conditions(self) -> str:
        if not self.daily.weathercode:
            return "Variable conditions"
        
        avg_code = mean(self.daily.weathercode)
        
        if avg_code < 3:
            return "Mostly clear skies"
        elif avg_code < 45:
            return "Partly cloudy"
        elif avg_code < 50:
            return "Foggy conditions"
        elif avg_code < 70:
            return "Rainy periods"
        elif avg_code < 80:
            return "Snow possible"
        else:
            return "Showers and possible storms"
    
    @computed_field
    @property
    def summary(self) -> str:
        return f"Average temperatures between {self.daily.avg_low:.0f}°C and {self.daily.avg_high:.0f}°C with {self.conditions.lower()}"
    
    @classmethod
    def from_api_response(
        cls,
        data: Dict,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Optional["WeatherForecast"]:
        daily_data = data.get("daily", {})
        if not daily_data:
            return None
        
        try:
            daily = DailyWeatherData(**daily_data)
            return cls(
                latitude=latitude,
                longitude=longitude,
                start_date=start_date,
                end_date=end_date,
                daily=daily
            )
        except Exception:
            return None

