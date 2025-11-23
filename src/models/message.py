"""Message model."""
from typing import Literal
from pydantic import BaseModel, Field


MessageRole = Literal["system", "user", "assistant"]


class Message(BaseModel):
    """Chat message model."""
    
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    
    class Config:
        """Pydantic configuration."""
        frozen = False
        extra = "forbid"
