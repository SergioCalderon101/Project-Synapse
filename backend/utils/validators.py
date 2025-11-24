"""Validators for input validation."""
import uuid
from typing import Optional


def validate_chat_id(chat_id: str) -> bool:
    """Validate that chat_id is a valid UUID.
    
    Args:
        chat_id: Chat ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        uuid.UUID(chat_id)
        return True
    except (ValueError, AttributeError):
        return False


def validate_model(model: Optional[str], default_model: str, supported_models: list) -> str:
    """Validate and return a supported model.
    
    Args:
        model: Model to validate
        default_model: Default model if invalid
        supported_models: List of supported models
        
    Returns:
        Validated model name
    """
    if not model or model not in supported_models:
        return default_model
    return model
