class WeatherContextTemplate:
    SOURCE = "Open-Meteo weather forecast"
    
    @staticmethod
    def format(weather_data: dict) -> str:
        return f"""<weather_data>
Location: {weather_data.get("location", "Unknown")}
Dates: {weather_data.get("start_date", "")} to {weather_data.get("end_date", "")}
Forecast: {weather_data.get("summary", "")}
Temperature Range: {weather_data.get("temp_range", "")}
Conditions: {weather_data.get("conditions", "")}
Source: {WeatherContextTemplate.SOURCE}
</weather_data>"""

