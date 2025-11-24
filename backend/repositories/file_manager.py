"""File management utilities for repositories."""
import json
from pathlib import Path
from typing import Optional, Any

from core.logging import get_logger

logger = get_logger(__name__)


class FileManager:
    """Gestor de archivos y directorios."""
    
    @staticmethod
    def ensure_directory_exists(directory: Path) -> None:
        """Asegura que un directorio exista, creándolo si es necesario.
        
        Args:
            directory: Path to directory
            
        Raises:
            OSError: If directory creation fails
        """
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio '{directory}' creado.")
            except OSError as e:
                logger.error(f"Error crítico: No se pudo crear '{directory}': {e}")
                raise
    
    @staticmethod
    def read_json_file(file_path: Path) -> Optional[Any]:
        """Lee un archivo JSON y retorna su contenido.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Parsed JSON content or None if error
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                # Validar que el contenido no esté vacío o sea None
                if content is None:
                    logger.warning(f"Archivo {file_path} contiene null")
                    return None
                return content
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error leyendo {file_path}: {e}")
            return None
        except Exception as e:
            logger.exception(f"Error inesperado leyendo {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json_file(file_path: Path, data: Any) -> bool:
        """Escribe datos en un archivo JSON.
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"Error escribiendo {file_path}: {e}")
            return False
