class VisaContextTemplate:
    SOURCE = "Travel Buddy API"
    
    @staticmethod
    def format(visa_data: dict) -> str:
        origin = visa_data.get("origin_country", "Unknown")
        destination = visa_data.get("destination_country", "Unknown")
        status = visa_data.get("status_description", "Unknown")
        stay_duration = visa_data.get("stay_duration")
        notes = visa_data.get("notes", "")
        evisa_link = visa_data.get("evisa_link")
        
        duration_info = f"\nMaximum Stay: {stay_duration}" if stay_duration else ""
        evisa_info = f"\neVisa Portal: {evisa_link}" if evisa_link else ""
        notes_info = f"\nNotes: {notes}" if notes else ""
        
        return f"""<visa_data>
Origin Country: {origin}
Destination Country: {destination}
Visa Requirement: {status}{duration_info}{evisa_info}{notes_info}
Source: {VisaContextTemplate.SOURCE}
</visa_data>"""

