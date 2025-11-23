"""Chat model."""
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

from models.message import Message


class ChatMetadata(BaseModel):
    """Chat metadata model."""
    
    id: str = Field(..., description="Chat UUID")
    title: str = Field("Nuevo Chat", description="Chat title")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp (ISO format)"
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp (ISO format)"
    )
    
    class Config:
        """Pydantic configuration."""
        frozen = False


class Chat(BaseModel):
    """Chat model with messages."""
    
    chat_id: str = Field(..., description="Chat UUID")
    messages: List[Message] = Field(default_factory=list, description="Chat messages")
    title: Optional[str] = Field(None, description="Chat title")
    
    class Config:
        """Pydantic configuration."""
        frozen = False
