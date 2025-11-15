import asyncio
import os

from app.modules.clients.ollama import OllamaClient
from app.algo.extractor.date import DateExtractor
from app.algo.extractor.location import LocationExtractor
from app.algo.extractor.intent import IntentExtractor
from app.models.extraction_result import ExtractionResult


class ExtractorManager:
    def __init__(self, llm_client: OllamaClient):
        self.llm = llm_client
    
    async def extract(self, message: str) -> ExtractionResult:
        intent_extractor = IntentExtractor(self.llm)
        location_extractor = LocationExtractor(self.llm)
        date_extractor = DateExtractor(self.llm)
        
        tasks = [
            ('intent', intent_extractor.extract(message)),
            ('location', location_extractor.extract(message)),
            ('date', date_extractor.extract(message))
        ]
        
        results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
        
        result_data = {}
        for (task_type, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                continue
            
            if result:
                result_data[task_type] = result
        
        return ExtractionResult(
            intent=result_data.get('intent'),
            location=result_data.get('location'),
            date=result_data.get('date')
        )

