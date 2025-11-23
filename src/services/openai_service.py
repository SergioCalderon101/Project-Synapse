"""OpenAI service for AI interactions."""
from typing import List, Optional, Dict, Any
from openai import APIError

from core.config import settings
from core.logging import get_logger
from models.message import Message

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""
    
    API_PARAMETERS = {
        "chat": {
            "temperature": 0.6,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        },
        "title": {
            "temperature": 0.3,
            "max_tokens": 20,
            "stop": None
        }
    }
    
    def __init__(self, openai_client):
        """Initialize OpenAI service.
        
        Args:
            openai_client: OpenAI client instance
        """
        self.client = openai_client
    
    def _get_api_parameters(self, purpose: str) -> Dict[str, Any]:
        """Get API parameters for specific purpose.
        
        Args:
            purpose: Purpose of API call ('chat' or 'title')
            
        Returns:
            Dictionary of API parameters
        """
        return self.API_PARAMETERS.get(purpose, self.API_PARAMETERS["chat"])
    
    def call_api(
        self,
        messages: List[Message],
        model: str,
        purpose: str = "chat"
    ) -> Optional[str]:
        """Call OpenAI Chat Completions API.
        
        Args:
            messages: List of messages
            model: Model name
            purpose: Purpose of call ('chat' or 'title')
            
        Returns:
            API response content or None if error
        """
        if not self.client:
            logger.error(f"Cliente OpenAI no inicializado ({purpose}).")
            return None
        
        try:
            # Convert Message objects to dict
            messages_dict = [msg.model_dump() for msg in messages]
            
            logger.debug(
                f"Enviando {len(messages)} mensajes a OpenAI "
                f"({purpose}, modelo: {model})"
            )
            
            params = {
                "model": model,
                "messages": messages_dict,
                **self._get_api_parameters(purpose)
            }
            
            response = self.client.chat.completions.create(**params)
            
            if not (response.choices and response.choices[0].message and
                    response.choices[0].message.content):
                logger.error(f"Respuesta inválida de OpenAI ({purpose}, {model})")
                return None
            
            reply = response.choices[0].message.content.strip()
            logger.debug(f"Respuesta recibida ({purpose}): '{reply[:100]}...'")
            return reply
        
        except APIError as e:
            logger.error(f"Error API OpenAI ({purpose}, {model}): {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error inesperado en OpenAI API ({purpose}): {e}")
            return None
    
    def generate_title(self, messages: List[Message]) -> Optional[str]:
        """Generate title for conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Generated title or None if error
        """
        # Get relevant messages (last 6 user/assistant messages)
        relevant_messages = [
            msg for msg in messages if msg.role in ["user", "assistant"]
        ][-6:]
        
        if not relevant_messages:
            logger.warning("No hay mensajes relevantes para generar título.")
            return None
        
        # Create title generation prompt
        title_messages = [
            Message(
                role="system",
                content="Eres un experto en resumir conversaciones concisamente."
            ),
            *relevant_messages,
            Message(
                role="user",
                content=(
                    f"Genera un título muy corto y descriptivo "
                    f"(máx ~5 palabras, {settings.max_title_length} chars) "
                    f"para esta conversación. Responde SOLO con el título."
                )
            )
        ]
        
        generated_title = self.call_api(
            title_messages,
            settings.openai_title_model,
            purpose="title"
        )
        
        if not generated_title:
            logger.error("Fallo al generar título.")
            return None
        
        # Clean and validate title
        cleaned_title = generated_title.replace('"', '').strip()
        cleaned_title = cleaned_title[:settings.max_title_length]
        
        # Reject generic or too short titles
        if (len(cleaned_title) > 3 and
                not cleaned_title.lower().startswith("conversación sobre")):
            logger.info(f"Título generado: '{cleaned_title}'")
            return cleaned_title
        
        logger.warning(f"Título rechazado: '{cleaned_title}' (genérico/corto)")
        return None
