"""Constants for visa-related functionality."""

VISA_API_BASE_URL = "https://rough-sun-2523.fly.dev"
VISA_API_TIMEOUT = 10.0
REST_COUNTRIES_TIMEOUT = 5.0
REST_COUNTRIES_BASE_URL = "https://restcountries.com/v3.1"

COUNTRY_NAME_TO_CODE = {
    "israel": "IL",
    "japan": "JP",
    "united states": "US",
    "usa": "US",
    "us": "US",
    "u.s.": "US",
    "u.s.a.": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "france": "FR",
    "germany": "DE",
    "spain": "ES",
    "italy": "IT",
    "canada": "CA",
    "australia": "AU",
    "china": "CN",
    "india": "IN",
    "brazil": "BR",
    "mexico": "MX",
    "thailand": "TH",
    "singapore": "SG",
    "south korea": "KR",
    "korea": "KR",
    "hong kong": "HK",
    "uae": "AE",
    "united arab emirates": "AE",
    "turkey": "TR",
    "egypt": "EG",
    "south africa": "ZA",
    "argentina": "AR",
    "chile": "CL",
    "peru": "PE",
    "colombia": "CO",
    "vietnam": "VN",
    "indonesia": "ID",
    "philippines": "PH",
    "malaysia": "MY",
    "new zealand": "NZ",
    "netherlands": "NL",
    "belgium": "BE",
    "switzerland": "CH",
    "austria": "AT",
    "sweden": "SE",
    "norway": "NO",
    "denmark": "DK",
    "finland": "FI",
    "poland": "PL",
    "portugal": "PT",
    "greece": "GR",
    "russia": "RU",
    "ukraine": "UA",
}

VISA_CATEGORY_TO_STATUS = {
    "VF": "no",
    "VOA": "visa_on_arrival",
    "EV": "evisa",
    "VR": "yes",
    "NA": "no_admission"
}

VISA_STATUS_DESCRIPTIONS = {
    "yes": "Visa required",
    "no": "No visa required",
    "visa_on_arrival": "Visa available on arrival",
    "evisa": "eVisa available",
    "no_admission": "No admission",
    "unknown": "Visa requirement information not available"
}

VISA_TEXT_KEYWORDS = {
    "no": ["no visa", "visa-free", "visa exempt"],
    "yes": ["visa required", "need a visa"],
    "visa_on_arrival": ["visa on arrival", "voa"],
    "evisa": ["evisa", "e-visa"]
}

DEFAULT_LLM_MODEL = "qwen3"
DEFAULT_LLM_TEMPERATURE = 0.1
DEFAULT_SOURCE = "llm"
MAX_TEXT_EXTRACT_LENGTH = 500

