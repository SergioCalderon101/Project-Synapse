"""Chat request/response schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from core.config import settings


class SendMessageRequest(BaseModel):
    """Request schema for sending a message."""
    
    mensaje: str = Field(..., description="User message")
    modelo: Optional[str] = Field(
        None,
        description="Model to use (defaults to configured model)"
    )
    
    @field_validator("mensaje")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message length."""
        v = v.strip()
        
        if len(v) < settings.min_message_length:
            raise ValueError("Mensaje vacío.")
        
        if len(v) > settings.max_message_length:
            raise ValueError(
                f"Mensaje demasiado largo. "
                f"Máximo {settings.max_message_length} caracteres."
            )
        
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "mensaje": "Hola, ¿cómo estás?",
                "modelo": "gpt-4o"
            }
        }


class MessageResponse(BaseModel):
    """Response schema for a message."""
    
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class SendMessageResponse(BaseModel):
    """Response schema for sending a message."""
    
    respuesta: str = Field(..., description="AI response")
    timestamp: str = Field(..., description="Response timestamp (ISO format)")
    new_title: Optional[str] = Field(None, description="New chat title if generated")


class CreateChatResponse(BaseModel):
    """Response schema for creating a chat."""
    
    chat_id: str = Field(..., description="Chat UUID")
    messages: List[MessageResponse] = Field(..., description="Initial messages")
    title: str = Field(..., description="Chat title")


class LoadChatResponse(BaseModel):
    """Response schema for loading a chat."""
    
    chat_id: str = Field(..., description="Chat UUID")
    messages: List[MessageResponse] = Field(..., description="Chat messages")
    title: str = Field(..., description="Chat title")


class ChatMetadataResponse(BaseModel):
    """Response schema for chat metadata."""
    
    id: str = Field(..., description="Chat UUID")
    title: str = Field(..., description="Chat title")
    created_at: str = Field(..., description="Creation timestamp")
    last_updated: str = Field(..., description="Last update timestamp")


class HistoryResponse(BaseModel):
    """Response schema for chat history."""
    
    history: List[ChatMetadataResponse] = Field(..., description="List of chats")


class DeleteChatResponse(BaseModel):
    """Response schema for deleting a chat."""
    
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str = Field(..., description="Error message")
