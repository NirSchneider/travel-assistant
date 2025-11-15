from fastapi import HTTPException

from app.models.message import ChatMessage
from app.models.response import ChatResponse
from app.services.conversation_handler import ConversationHandler


class ConversationController:
    def __init__(self, conversation_service: ConversationHandler):
        self.service = conversation_service
    
    async def chat(self, message: ChatMessage) -> ChatResponse:
        try:
            response = await self.service.handle(message.message)
            
            return ChatResponse(
                response=response,
            )
        
        except Exception as e:
            print(f"Error in chat endpoint: {str(e)}")
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again."
            )
    
    async def reset_conversation(self) -> str:
        try:
            self.service.start_conversation()
            return "Conversation successfully reset"
        except Exception as e:
            print(f"Error resetting conversation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error resetting conversation: {str(e)}"
            )
