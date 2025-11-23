"""Chat service for business logic."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from core.config import settings
from core.logging import get_logger
from models.message import Message
from models.chat import Chat, ChatMetadata
from repositories.chat_repository import ChatRepository
from repositories.metadata_repository import MetadataRepository
from services.openai_service import OpenAIService

logger = get_logger(__name__)


class ChatService:
    """Service for chat business logic."""
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        metadata_repo: MetadataRepository,
        openai_service: OpenAIService
    ):
        """Initialize chat service.
        
        Args:
            chat_repo: Chat repository
            metadata_repo: Metadata repository
            openai_service: OpenAI service
        """
        self.chat_repo = chat_repo
        self.metadata_repo = metadata_repo
        self.openai_service = openai_service
    
    def _get_system_message(self) -> Message:
        """Get default system message.
        
        Returns:
            System message
        """
        return Message(role="system", content=settings.default_system_message)
    
    def _ensure_system_message(self, messages: List[Message]) -> List[Message]:
        """Ensure messages have system prompt.
        
        Args:
            messages: List of messages
            
        Returns:
            Messages with system prompt
        """
        if not messages or messages[0].role != "system":
            return [self._get_system_message()] + (messages or [])
        
        # Update system message if different
        if messages[0].content != settings.default_system_message:
            messages[0].content = settings.default_system_message
        
        return messages
    
    def _apply_context_limit(self, messages: List[Message]) -> List[Message]:
        """Apply context window limit.
        
        Args:
            messages: List of messages
            
        Returns:
            Truncated messages
        """
        if len(messages) <= settings.max_context_length:
            return messages
        
        # Keep system message
        system_message = (
            [messages[0]] if messages and messages[0].role == "system" else []
        )
        
        # Keep last N user/assistant messages
        user_assistant_msgs = [msg for msg in messages if msg.role != "system"]
        msgs_to_keep = max(0, settings.max_context_length - len(system_message))
        limited_messages = system_message + user_assistant_msgs[-msgs_to_keep:]
        
        logger.debug(
            f"Contexto truncado de {len(messages)} a {len(limited_messages)} mensajes."
        )
        return limited_messages
    
    def create_chat(self) -> Tuple[str, List[Message], str]:
        """Create a new chat.
        
        Returns:
            Tuple of (chat_id, messages, title)
        """
        chat_id = str(uuid.uuid4())
        messages = [self._get_system_message()]
        
        # Save chat messages
        self.chat_repo.save(chat_id, messages)
        
        # Save metadata
        now_iso = datetime.now(timezone.utc).isoformat()
        metadata = ChatMetadata(
            id=chat_id,
            title="Nuevo Chat",
            created_at=now_iso,
            last_updated=now_iso
        )
        self.metadata_repo.update(chat_id, metadata)
        
        logger.info(f"Nuevo chat creado: {chat_id}")
        return chat_id, messages, "Nuevo Chat"
    
    def get_chat(self, chat_id: str) -> Optional[Chat]:
        """Get a specific chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            Chat or None if not found
        """
        messages = self.chat_repo.load(chat_id)
        if messages is None:
            return None
        
        # Ensure system message and apply context limit
        messages = self._ensure_system_message(messages)
        messages = self._apply_context_limit(messages)
        
        # Get metadata
        metadata = self.metadata_repo.get(chat_id)
        title = metadata.title if metadata else f"Chat {chat_id[:8]}..."
        
        logger.debug(f"Chat {chat_id} cargado. Título: {title}")
        return Chat(chat_id=chat_id, messages=messages, title=title)
    
    def get_history(self) -> List[ChatMetadata]:
        """Get chat history.
        
        Returns:
            List of chat metadata sorted by last_updated
        """
        metadata = self.metadata_repo.load()
        history_list = sorted(
            metadata.values(),
            key=lambda m: m.last_updated,
            reverse=True
        )
        logger.debug(f"Historial solicitado: {len(history_list)} chats")
        return history_list
    
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            True if deleted, False if not found
        """
        metadata_deleted = self.metadata_repo.delete(chat_id)
        file_deleted = self.chat_repo.delete(chat_id)
        
        if metadata_deleted or file_deleted:
            logger.info(f"Chat {chat_id} eliminado.")
            return True
        
        return False
    
    def process_message(
        self,
        chat_id: str,
        user_message: str,
        model: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Process a user message and generate AI response.
        
        Args:
            chat_id: Chat UUID
            user_message: User's message
            model: Model to use
            
        Returns:
            Tuple of (response, timestamp, new_title)
            Returns (None, None, None) if error
        """
        # Load messages
        messages = self.chat_repo.load(chat_id)
        if messages is None:
            logger.warning(f"Chat inexistente o corrupto: {chat_id}")
            return None, None, None
        
        # Ensure system message
        messages = self._ensure_system_message(messages)
        
        # Validate model
        validated_model = settings.validate_openai_model(model)
        logger.info(f"Procesando mensaje (chat: {chat_id}, modelo: {validated_model})")
        
        # Add user message
        messages.append(Message(role="user", content=user_message))
        
        # Apply context limit for API call
        messages_for_api = self._apply_context_limit(messages)
        
        # Call OpenAI
        assistant_reply = self.openai_service.call_api(
            messages_for_api,
            validated_model,
            purpose="chat"
        )
        
        if assistant_reply is None:
            logger.error(f"Llamada API fallida (chat: {chat_id})")
            return None, None, None
        
        # Add assistant response
        messages.append(Message(role="assistant", content=assistant_reply))
        
        # Update title if needed
        new_title = self._update_title_if_needed(chat_id, messages)
        
        # Save messages
        messages_to_save = self._apply_context_limit(messages)
        if not self.chat_repo.save(chat_id, messages_to_save):
            logger.error(
                f"Error guardando mensajes después de respuesta (chat: {chat_id})"
            )
        
        # Return response
        now_iso = datetime.now(timezone.utc).isoformat()
        logger.info(f"Respuesta enviada (chat: {chat_id}, modelo: {validated_model})")
        return assistant_reply, now_iso, new_title
    
    def _update_title_if_needed(
        self,
        chat_id: str,
        messages: List[Message]
    ) -> Optional[str]:
        """Update chat title if needed.
        
        Args:
            chat_id: Chat UUID
            messages: Current messages
            
        Returns:
            New title or None
        """
        metadata = self.metadata_repo.get(chat_id)
        if not metadata:
            logger.warning(f"Metadata no encontrada para {chat_id}")
            return None
        
        # Count non-system messages
        message_count = len([m for m in messages if m.role != "system"])
        min_messages = settings.title_generation_min_messages - 1
        
        # Generate title if conditions met
        if metadata.title == "Nuevo Chat" and message_count >= min_messages:
            logger.info(f"Generando título para chat {chat_id}...")
            new_title = self.openai_service.generate_title(messages)
            
            if new_title:
                # Update metadata
                metadata.title = new_title
                metadata.last_updated = datetime.now(timezone.utc).isoformat()
                self.metadata_repo.update(chat_id, metadata)
                return new_title
            
            logger.warning(f"Fallo al generar título para {chat_id}")
        else:
            # Just update timestamp
            metadata.last_updated = datetime.now(timezone.utc).isoformat()
            self.metadata_repo.update(chat_id, metadata)
        
        return None
