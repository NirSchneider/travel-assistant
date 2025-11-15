"""API router configuration."""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

from app.models.message import ChatMessage
from app.models.response import ChatResponse
from app.api.controllers.conversation_controller import ConversationController

v1 = APIRouter(tags=["v1"], prefix="/api/v1")


def create_travel_assistant_router(controller: ConversationController):
    travel_assistant_router = APIRouter(tags=["travel-assistant"], prefix="/travel-assistant")

    @travel_assistant_router.post("/chat", response_model=ChatResponse)
    async def chat(message: ChatMessage) -> ChatResponse:
        return await controller.chat(message)

    @travel_assistant_router.post("/reset")
    async def reset_conversation():
        return await controller.reset_conversation()

    return travel_assistant_router


def create_static_router(static_dir: Path):
    static_router = APIRouter(tags=["static"])

    @static_router.get("/", response_class=HTMLResponse)
    async def read_root():
        try:
            index_path = static_dir / "index.html"
            with open(index_path, "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(
                content="<h1>Chat interface not found</h1><p>Please ensure app/static/index.html exists.</p>",
                status_code=404
            )

    @static_router.get("/static/{file_path:path}")
    async def serve_static(file_path: str):
        try:
            file_full_path = static_dir / file_path
            response = FileResponse(str(file_full_path))
            if file_path.endswith('.js'):
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
            return response
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")

    return static_router
