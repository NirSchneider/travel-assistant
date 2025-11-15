from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractionResult:
    intent: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def get(self, key: str, default=None):
        return getattr(self, key, default)

