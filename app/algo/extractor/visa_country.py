import re
from typing import Optional, Tuple
from app.models.extraction_result import ExtractionResult


class VisaCountryExtractor:
    
    @staticmethod
    def extract_countries(
        user_message: str,
        extraction_result: ExtractionResult
    ) -> Tuple[Optional[str], Optional[str]]:
        origin_country = None
        destination_country = None
        user_lower = user_message.lower()
        
        # Pattern 1: "do i need visa from [origin] to [destination]"
        # Match country names (1-3 words max) after "from" and before "to"
        pattern1 = r"do\s+i\s+need\s+visa\s+from\s+([a-z]+(?:\s+[a-z]+){0,2}?)\s+to\s+([a-z]+(?:\s+[a-z]+){0,2}?)(?:\s|$|[?])"
        match = re.search(pattern1, user_lower)
        if match:
            origin_country = match.group(1).strip()
            destination_country = match.group(2).strip()
        
        # Pattern 2: "does [origin] need visa to [destination]"
        if not origin_country or not destination_country:
            pattern2 = r"does\s+([a-z]+(?:\s+[a-z]+){0,2}?)\s+need\s+(?:visa|passport)\s+(?:to|for)\s+([a-z]+(?:\s+[a-z]+){0,2}?)(?:\s|$|[?])"
            match = re.search(pattern2, user_lower)
            if match:
                origin_country = match.group(1).strip()
                destination_country = match.group(2).strip()
        
        # Pattern 3: "visa from [origin] to [destination]"
        if not origin_country or not destination_country:
            pattern3 = r"visa\s+from\s+([a-z]+(?:\s+[a-z]+){0,2}?)\s+to\s+([a-z]+(?:\s+[a-z]+){0,2}?)(?:\s|$|[?])"
            match = re.search(pattern3, user_lower)
            if match:
                origin_country = match.group(1).strip()
                destination_country = match.group(2).strip()
        
        # Pattern 4: "visa for [destination]" or "visa to [destination]"
        if not origin_country or not destination_country:
            pattern4 = r"visa\s+(?:for|to)\s+([^?\s]+(?:\s+[^?\s]+)*?)[?]?"
            match = re.search(pattern4, user_lower)
            if match:
                destination_country = match.group(1).strip()
                if extraction_result.location:
                    origin_country = extraction_result.location
        
        # Pattern 5: "[origin] to [destination]" (simple pattern)
        if not origin_country or not destination_country:
            pattern5 = r"(?:^|\s)([^?\s]+(?:\s+[^?\s]+)*?)\s+to\s+([^?\s]+(?:\s+[^?\s]+)*?)(?:\s|$|[?])"
            match = re.search(pattern5, user_lower)
            if match:
                if "visa" not in match.group(0) and "need" not in match.group(0):
                    origin_country = match.group(1).strip()
                    destination_country = match.group(2).strip()
        
        if origin_country:
            origin_country = re.sub(r'\b(do|i|need|visa|from|to|for|a|an|the)\b', '', origin_country, flags=re.IGNORECASE).strip()
            origin_country = ' '.join(origin_country.split())
        
        if destination_country:
            destination_country = re.sub(r'\b(do|i|need|visa|from|to|for|a|an|the)\b', '', destination_country, flags=re.IGNORECASE).strip()
            destination_country = ' '.join(destination_country.split())
             
        return origin_country, destination_country

