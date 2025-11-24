"""Metadata repository for chat metadata management."""
from typing import Dict
from pathlib import Path
from filelock import FileLock

from core.config import settings
from core.logging import get_logger
from models.chat import ChatMetadata
from repositories.file_manager import FileManager

logger = get_logger(__name__)


class MetadataRepository:
    """Repository for managing chat metadata."""
    
    def __init__(
        self,
        metadata_file: Path = settings.metadata_file,
        lock_file: Path = settings.metadata_lock_file
    ):
        """Initialize metadata repository.
        
        Args:
            metadata_file: Path to metadata JSON file
            lock_file: Path to lock file
        """
        self.metadata_file = metadata_file
        self.lock_file = lock_file
        self.lock = FileLock(str(lock_file))
        self.file_manager = FileManager()
    
    def load(self) -> Dict[str, ChatMetadata]:
        """Carga metadata desde archivo con protección de lock.
        
        Returns:
            Dictionary of chat_id -> ChatMetadata
        """
        self.file_manager.ensure_directory_exists(self.metadata_file.parent)
        metadata = {}
        
        try:
            with self.lock.acquire(timeout=5):
                loaded_data = self.file_manager.read_json_file(self.metadata_file)
                
                if loaded_data and isinstance(loaded_data, dict):
                    # Convert dict to ChatMetadata objects
                    for chat_id, data in loaded_data.items():
                        try:
                            metadata[chat_id] = ChatMetadata(**data)
                        except Exception as e:
                            logger.error(f"Error parsing metadata for {chat_id}: {e}")
                elif loaded_data is not None:
                    logger.warning(
                        f"{self.metadata_file} contiene datos inválidos. Reiniciando."
                    )
        except TimeoutError:
            logger.error(f"Timeout esperando lock para leer {self.metadata_file}.")
        except Exception as e:
            logger.exception(f"Error inesperado cargando metadata: {e}")
        
        return metadata
    
    def save(self, metadata: Dict[str, ChatMetadata]) -> None:
        """Guarda metadata en archivo con protección de lock.
        
        Args:
            metadata: Dictionary of chat_id -> ChatMetadata
        """
        self.file_manager.ensure_directory_exists(self.metadata_file.parent)
        
        try:
            with self.lock.acquire(timeout=5):
                # Convert ChatMetadata objects to dict
                data_dict = {
                    chat_id: meta.model_dump()
                    for chat_id, meta in metadata.items()
                }
                
                if self.file_manager.write_json_file(self.metadata_file, data_dict):
                    logger.debug(
                        f"Metadata guardada en {self.metadata_file} "
                        f"({len(metadata)} chats)"
                    )
        except TimeoutError:
            logger.error(f"Timeout esperando lock para guardar {self.metadata_file}.")
        except Exception as e:
            logger.exception(f"Error inesperado guardando metadata: {e}")
    
    def get(self, chat_id: str) -> ChatMetadata | None:
        """Get metadata for a specific chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            ChatMetadata or None if not found
        """
        metadata = self.load()
        return metadata.get(chat_id)
    
    def update(self, chat_id: str, metadata: ChatMetadata) -> None:
        """Update metadata for a specific chat.
        
        Args:
            chat_id: Chat UUID
            metadata: Updated metadata
        """
        all_metadata = self.load()
        all_metadata[chat_id] = metadata
        self.save(all_metadata)
    
    def delete(self, chat_id: str) -> bool:
        """Delete metadata for a specific chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            True if deleted, False if not found
        """
        metadata = self.load()
        if chat_id in metadata:
            del metadata[chat_id]
            self.save(metadata)
            return True
        return False
