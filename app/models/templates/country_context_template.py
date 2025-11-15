class CountryContextTemplate:    
    SOURCE = "REST Countries API"
    
    @staticmethod
    def format(country_data: dict) -> str:
        languages = ", ".join(country_data.get("languages", []))
        
        return f"""<country_data>
Country: {country_data.get("name", "Unknown")}
Capital: {country_data.get("capital", "Unknown")}
Region: {country_data.get("region", "Unknown")}
Currency: {country_data.get("currency", "Unknown")}
Languages: {languages}
Timezone: {country_data.get("timezone", "Unknown")}
Source: {CountryContextTemplate.SOURCE}
</country_data>"""

