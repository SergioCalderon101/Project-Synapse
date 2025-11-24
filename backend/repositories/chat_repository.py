"""Chat repository for chat message management."""
from typing import List, Optional
from pathlib import Path

from core.config import settings
from core.logging import get_logger
from models.message import Message
from repositories.file_manager import FileManager

logger = get_logger(__name__)


class ChatRepository:
    """Repository for managing chat messages."""
    
    def __init__(self, chats_dir: Path = settings.chats_dir):
        """Initialize chat repository.
        
        Args:
            chats_dir: Directory for chat storage
        """
        self.chats_dir = chats_dir
        self.file_manager = FileManager()
    
    def _get_chat_file_path(self, chat_id: str) -> Path:
        """Get file path for a chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            Path to chat file
        """
        return self.chats_dir / f"{chat_id}.json"
    
    def load(self, chat_id: str) -> Optional[List[Message]]:
        """Load messages for a chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            List of messages or None if not found/invalid
        """
        self.file_manager.ensure_directory_exists(self.chats_dir)
        chat_file = self._get_chat_file_path(chat_id)
        
        messages_data = self.file_manager.read_json_file(chat_file)
        
        if messages_data is None:
            logger.warning(f"Archivo de chat no encontrado: {chat_file}")
            return None
        
        if not isinstance(messages_data, list):
            logger.error(f"Chat {chat_file} con formato inválido (no es lista).")
            return None
        
        # Convert to Message objects
        try:
            messages = [Message(**msg) for msg in messages_data]
            logger.debug(f"Chat {chat_id} cargado ({len(messages)} mensajes).")
            return messages
        except Exception as e:
            logger.error(f"Error parsing messages for {chat_id}: {e}")
            return None
    
    def save(self, chat_id: str, messages: List[Message]) -> bool:
        """Save messages for a chat.
        
        Args:
            chat_id: Chat UUID
            messages: List of messages
            
        Returns:
            True if successful, False otherwise
        """
        self.file_manager.ensure_directory_exists(self.chats_dir)
        chat_file = self._get_chat_file_path(chat_id)
        
        # Convert Message objects to dict
        messages_dict = [msg.model_dump() for msg in messages]
        
        if self.file_manager.write_json_file(chat_file, messages_dict):
            logger.debug(f"Chat {chat_id} guardado ({len(messages)} mensajes).")
            return True
        
        logger.error(f"Error guardando chat {chat_id}")
        return False
    
    def delete(self, chat_id: str) -> bool:
        """Delete a chat file.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            True if deleted, False if not found or error
        """
        chat_file = self._get_chat_file_path(chat_id)
        
        if chat_file.exists():
            try:
                chat_file.unlink()
                logger.info(f"Archivo eliminado: {chat_file}")
                return True
            except (OSError, PermissionError) as e:
                logger.error(f"Error eliminando archivo {chat_file}: {e}")
                return False
        
        return False
    
    def exists(self, chat_id: str) -> bool:
        """Check if a chat exists.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            True if chat exists, False otherwise
        """
        chat_file = self._get_chat_file_path(chat_id)
        return chat_file.exists()
