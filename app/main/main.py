from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from app.modules.clients.ollama import OllamaClient
from app.services.conversation_handler import ConversationHandler
from app.api.controllers.conversation_controller import ConversationController
from app.api.router import create_travel_assistant_router, create_static_router

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "app" / "static"

llm_client = OllamaClient()
conversation_service = ConversationHandler(llm_client)
conversation_controller = ConversationController(conversation_service)
travel_assistant_router = create_travel_assistant_router(conversation_controller)
static_router = create_static_router(STATIC_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    conversation_service.start_conversation()
    yield

fast_api = FastAPI(lifespan=lifespan)
fast_api.include_router(travel_assistant_router)
fast_api.include_router(static_router)


def main():
    uvicorn.run(fast_api, host='0.0.0.0', port=8000)


if __name__ == "__main__":
    main()

