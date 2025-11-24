"""Dependency injection and instance management."""
from typing import Optional
from openai import OpenAI

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class Dependencies:
    """Container for application dependencies."""
    
    def __init__(self):
        """Initialize dependencies."""
        self._openai_client: Optional[OpenAI] = None
    
    @property
    def openai_client(self) -> Optional[OpenAI]:
        """Get OpenAI client instance (lazy initialization)."""
        if self._openai_client is None:
            self._openai_client = self._create_openai_client()
        return self._openai_client
    
    def _create_openai_client(self) -> Optional[OpenAI]:
        """Create OpenAI client instance.
        
        Returns:
            OpenAI client or None if API key not configured
        """
        if not settings.openai_api_key:
            logger.warning(
                "OPENAI_APIKEY no encontrada. Funcionalidad AI deshabilitada."
            )
            return None
        
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            logger.info("Cliente OpenAI inicializado.")
            logger.debug(
                f"Modelo Chat: {settings.openai_chat_model}, "
                f"Modelo Título: {settings.openai_title_model}"
            )
            return client
        except Exception as e:
            logger.exception(f"Error inicializando OpenAI: {e}")
            return None
    
    def reset(self):
        """Reset all dependencies (useful for testing)."""
        self._openai_client = None


# Global dependencies instance
dependencies = Dependencies()
