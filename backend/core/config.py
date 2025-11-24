"""Application configuration management."""
from typing import Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_APIKEY")
    openai_chat_model: str = Field("gpt-3.5-turbo", alias="OPENAI_CHAT_MODEL")
    openai_title_model: str = Field("gpt-3.5-turbo", alias="OPENAI_TITLE_MODEL")
    
    # Supported models
    supported_openai_models: List[str] = [
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4",
        "gpt-4o-mini"
    ]
    
    # Flask Configuration
    flask_debug: bool = Field(False, alias="FLASK_DEBUG")
    port: int = Field(5000, alias="PORT")
    host: str = Field("0.0.0.0", alias="HOST")
    
    # CORS Configuration
    cors_origins: str = Field("*", alias="CORS_ORIGINS")
    
    # Logging Configuration
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    
    # Directory Configuration
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    
    @property
    def chats_dir(self) -> Path:
        """Chat storage directory."""
        return self.base_dir / "data" / "chats"
    
    @property
    def metadata_file(self) -> Path:
        """Metadata file path."""
        return self.chats_dir / "chats_metadata.json"
    
    @property
    def metadata_lock_file(self) -> Path:
        """Metadata lock file path."""
        return self.chats_dir / "metadata.lock"
    
    @property
    def static_folder(self) -> Path:
        """Static files directory."""
        return self.base_dir.parent / "frontend" / "static"
    
    @property
    def templates_folder(self) -> Path:
        """Templates directory."""
        return self.base_dir.parent / "frontend" / "templates"
    
    @property
    def logs_folder(self) -> Path:
        """Logs directory."""
        return self.base_dir / "data" / "logs"
    
    @property
    def log_file(self) -> Path:
        """Log file path."""
        return self.logs_folder / "app.log"
    
    # Chat Configuration
    max_title_length: int = 40
    max_context_length: int = 12
    title_generation_min_messages: int = 5
    
    # Input Validation
    max_message_length: int = 4000
    min_message_length: int = 1
    
    # Rate Limiting
    rate_limit_per_day: int = 200
    rate_limit_per_hour: int = 50
    rate_limit_chat_per_minute: int = 30
    
    # Default System Message
    default_system_message: str = """Eres Synapse AI, un asistente inteligente, adaptable y profesional. Tu propósito es proporcionar ayuda útil, precisa y contextualmente apropiada a cada usuario.

## Principios Fundamentales

**Análisis Inteligente:**
- Evalúa cada consulta en su contexto completo
- Identifica la intención real del usuario más allá de las palabras exactas
- Adapta tu enfoque según la complejidad y naturaleza de la solicitud
- Para problemas complejos, descompón en pasos lógicos cuando sea útil

**Comunicación Efectiva:**
- Sé directo y conciso, pero completo
- Estructura tu respuesta de manera clara y lógica
- Usa formato Markdown apropiadamente para mejorar la legibilidad
- Adapta tu tono al contexto (técnico, casual, formal según corresponda)
- Evita redundancias y información innecesaria

**Gestión de Contexto:**
- Mantén coherencia con el historial de conversación
- Construye sobre intercambios anteriores de manera inteligente
- Pide clarificaciones solo cuando realmente agreguen valor
- Recuerda preferencias y patrones del usuario cuando sea relevante

**Manejo de Contenido:**
- Genera contenido completo y bien estructurado en tu respuesta
- Organiza información compleja usando encabezados, listas y formatos apropiados
- Proporciona ejemplos prácticos cuando sea útil
- Incluye consideraciones importantes o limitaciones cuando sea relevante

**Resolución de Problemas:**
- Si una solicitud es ambigua, ofrece la interpretación más probable y menciona alternativas si es necesario
- Para errores o problemas técnicos, proporciona diagnóstico y soluciones paso a paso
- Adapta el nivel de detalle técnico al conocimiento aparente del usuario
- Sugiere mejores prácticas cuando sea apropiado

**Calidad y Precisión:**
- Prioriza respuestas precisas sobre respuestas rápidas
- Reconoce abiertamente las limitaciones de tu conocimiento
- Para información que cambia frecuentemente, sugiere verificación cuando sea apropiado
- Mantén objetividad, especialmente en temas controvertidos

## Comportamientos Adaptativos

- **Consultas técnicas:** Proporciona detalles técnicos precisos, código limpio, y explica conceptos complejos
- **Solicitudes creativas:** Ofrece ideas originales y bien desarrolladas
- **Problemas de análisis:** Presenta razonamiento estructurado y considera múltiples perspectivas
- **Tareas de escritura:** Crea contenido apropiado para el propósito y audiencia especificados

Tu objetivo es ser genuinamente útil adaptándote inteligentemente a las necesidades específicas de cada interacción."""
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v_upper
    
    @field_validator("openai_chat_model", "openai_title_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate OpenAI model."""
        # Get the instance to access supported_openai_models
        # During validation, we can't access other fields easily
        # So we'll do basic validation here and comprehensive in the service
        return v
    
    def validate_openai_model(self, model: str) -> str:
        """Validate that the model is supported."""
        if model not in self.supported_openai_models:
            return self.openai_chat_model
        return model
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        """Pydantic configuration."""
        env_file = str(Path(__file__).parent.parent.parent / "config" / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
