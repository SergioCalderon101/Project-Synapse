"""Synapse AI - Aplicación de chat con IA usando OpenAI API."""
import os
import json
import uuid
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from flask import Flask, request, jsonify, render_template, abort
from flask_cors import CORS
from openai import OpenAI, APIError
from dotenv import load_dotenv
from filelock import FileLock

# Configuración
load_dotenv()


class Config:
    """Configuración centralizada de la aplicación."""
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_APIKEY")

    SUPPORTED_OPENAI_MODELS = [
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4",
        "gpt-4o-mini"
    ]

    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
    OPENAI_TITLE_MODEL: str = os.getenv("OPENAI_TITLE_MODEL", "gpt-3.5-turbo")

    # Directorios
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    CHATS_DIR: str = os.path.join(BASE_DIR, "chats")
    METADATA_FILE: str = os.path.join(CHATS_DIR, "chats_metadata.json")
    METADATA_LOCK_FILE: str = os.path.join(CHATS_DIR, "metadata.lock")
    STATIC_FOLDER: str = os.path.join(BASE_DIR, "static")
    TEMPLATES_FOLDER: str = os.path.join(BASE_DIR, "templates")
    LOGS_FOLDER: str = os.path.join(BASE_DIR, "logs")
    LOG_FILE: str = os.path.join(LOGS_FOLDER, "app.log")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    PORT: int = int(os.getenv("PORT", "5000"))

    # Chat
    MAX_TITLE_LENGTH: int = 40
    MAX_CONTEXT_LENGTH: int = 12
    TITLE_GENERATION_MIN_MESSAGES: int = 5

    @classmethod
    def validate_model(cls, model: str) -> str:
        """Valida que el modelo esté soportado."""
        if model not in cls.SUPPORTED_OPENAI_MODELS:
            return cls.OPENAI_CHAT_MODEL
        return model

    DEFAULT_SYSTEM_MESSAGE: Dict[str, str] = {
        "role": "system",
        "content": """Eres Synapse AI, un asistente inteligente, adaptable y profesional. Tu propósito es proporcionar ayuda útil, precisa y contextualmente apropiada a cada usuario.\n\n## Principios Fundamentales\n\n**Análisis Inteligente:**\n- Evalúa cada consulta en su contexto completo\n- Identifica la intención real del usuario más allá de las palabras exactas\n- Adapta tu enfoque según la complejidad y naturaleza de la solicitud\n- Para problemas complejos, descompón en pasos lógicos cuando sea útil\n\n**Comunicación Efectiva:**\n- Sé directo y conciso, pero completo\n- Estructura tu respuesta de manera clara y lógica\n- Usa formato Markdown apropiadamente para mejorar la legibilidad\n- Adapta tu tono al contexto (técnico, casual, formal según corresponda)\n- Evita redundancias y información innecesaria\n\n**Gestión de Contexto:**\n- Mantén coherencia con el historial de conversación\n- Construye sobre intercambios anteriores de manera inteligente\n- Pide clarificaciones solo cuando realmente agreguen valor\n- Recuerda preferencias y patrones del usuario cuando sea relevante\n\n**Manejo de Contenido:**\n- Genera contenido completo y bien estructurado en tu respuesta\n- Organiza información compleja usando encabezados, listas y formatos apropiados\n- Proporciona ejemplos prácticos cuando sea útil\n- Incluye consideraciones importantes o limitaciones cuando sea relevante\n\n**Resolución de Problemas:**\n- Si una solicitud es ambigua, ofrece la interpretación más probable y menciona alternativas si es necesario\n- Para errores o problemas técnicos, proporciona diagnóstico y soluciones paso a paso\n- Adapta el nivel de detalle técnico al conocimiento aparente del usuario\n- Sugiere mejores prácticas cuando sea apropiado\n\n**Calidad y Precisión:**\n- Prioriza respuestas precisas sobre respuestas rápidas\n- Reconoce abiertamente las limitaciones de tu conocimiento\n- Para información que cambia frecuentemente, sugiere verificación cuando sea apropiado\n- Mantén objetividad, especialmente en temas controvertidos\n\n## Comportamientos Adaptativos\n\n- **Consultas técnicas:** Proporciona detalles técnicos precisos, código limpio, y explica conceptos complejos\n- **Solicitudes creativas:** Ofrece ideas originales y bien desarrolladas\n- **Problemas de análisis:** Presenta razonamiento estructurado y considera múltiples perspectivas\n- **Tareas de escritura:** Crea contenido apropiado para el propósito y audiencia especificados\n\nTu objetivo es ser genuinamente útil adaptándote inteligentemente a las necesidades específicas de cada interacción."""
    }


config = Config()

# Inicialización de Flask
app = Flask(
    __name__, 
    template_folder=config.TEMPLATES_FOLDER,
    static_folder=config.STATIC_FOLDER
)


def setup_cors() -> None:
    """Configura CORS para la aplicación."""
    cors_origins = (
        config.CORS_ORIGINS.split(',') 
        if config.CORS_ORIGINS != "*" 
        else "*"
    )
    CORS(app, origins=cors_origins, supports_credentials=True)


def setup_logging() -> None:
    """Configura el sistema de logging."""
    # Crear carpeta de logs
    if not os.path.exists(config.LOGS_FOLDER):
        try:
            os.makedirs(config.LOGS_FOLDER)
        except OSError as e:
            print(
                f"CRITICAL: No se pudo crear carpeta de logs '{config.LOGS_FOLDER}': {e}",
                file=sys.stderr
            )
            sys.exit(1)

    # Formatter
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s'
    )

    # Stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    app.logger.addHandler(stream_handler)

    # File handler
    try:
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_formatter)
        app.logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        print(
            f"WARNING: No se pudo configurar logging a archivo '{config.LOG_FILE}': {e}",
            file=sys.stderr
        )

    app.logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    app.logger.propagate = False


def setup_openai_client() -> Optional[OpenAI]:
    """Configura el cliente de OpenAI."""
    # Solo inicializar en el proceso principal (no en el reloader)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' and config.FLASK_DEBUG:
        # En el proceso hijo del reloader, reinicializar silenciosamente
        if config.OPENAI_API_KEY:
            return OpenAI(api_key=config.OPENAI_API_KEY)
        return None

    # Proceso principal
    if not config.OPENAI_API_KEY:
        app.logger.warning(
            "OPENAI_APIKEY no encontrada. Funcionalidad AI deshabilitada."
        )
        return None

    try:
        openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        app.logger.info("Cliente OpenAI inicializado.")
        app.logger.debug(
            f"Modelo Chat: {config.OPENAI_CHAT_MODEL}, "
            f"Modelo Título: {config.OPENAI_TITLE_MODEL}"
        )
        return openai_client
    except Exception as e:
        app.logger.exception(f"Error inicializando OpenAI: {e}")
        return None


# Configurar aplicación
setup_cors()
setup_logging()
client = setup_openai_client()

# Clases auxiliares


class FileManager:
    """Gestor de archivos y directorios."""

    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        """Asegura que un directorio exista, creándolo si es necesario."""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                app.logger.info(f"Directorio '{directory}' creado.")
            except OSError as e:
                app.logger.error(f"Error crítico: No se pudo crear '{directory}': {e}")
                raise

    @staticmethod
    def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """Lee un archivo JSON y retorna su contenido."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                # Validar que el contenido no esté vacío o sea None
                if content is None:
                    app.logger.warning(f"Archivo {file_path} contiene null")
                    return None
                return content
        except (IOError, json.JSONDecodeError) as e:
            app.logger.error(f"Error leyendo {file_path}: {e}")
            return None
        except Exception as e:
            app.logger.exception(f"Error inesperado leyendo {file_path}: {e}")
            return None

    @staticmethod
    def write_json_file(file_path: str, data: Any) -> bool:
        """Escribe datos en un archivo JSON."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            app.logger.error(f"Error escribiendo {file_path}: {e}")
            return False


class MetadataManager:
    """Gestor de metadata de chats con soporte de locks."""

    def __init__(self):
        self.lock = FileLock(config.METADATA_LOCK_FILE)

    def load(self) -> Dict[str, Dict[str, Any]]:
        """Carga metadata desde archivo con protección de lock."""
        FileManager.ensure_directory_exists(config.CHATS_DIR)
        metadata = {}

        try:
            with self.lock.acquire(timeout=5):
                loaded_data = FileManager.read_json_file(config.METADATA_FILE)
                
                if loaded_data and isinstance(loaded_data, dict):
                    metadata = loaded_data
                elif loaded_data is not None:
                    app.logger.warning(
                        f"{config.METADATA_FILE} contiene datos inválidos. Reiniciando.")
        except TimeoutError:
            app.logger.error(f"Timeout esperando lock para leer {config.METADATA_FILE}.")
        except Exception as e:
            app.logger.exception(f"Error inesperado cargando metadata: {e}")

        return metadata

    def save(self, metadata: Dict[str, Dict[str, Any]]) -> None:
        """Guarda metadata en archivo con protección de lock."""
        FileManager.ensure_directory_exists(config.CHATS_DIR)

        try:
            with self.lock.acquire(timeout=5):
                if FileManager.write_json_file(config.METADATA_FILE, metadata):
                    app.logger.debug(
                        f"Metadata guardada en {config.METADATA_FILE} ({len(metadata)} chats)")
        except TimeoutError:
            app.logger.error(f"Timeout esperando lock para guardar {config.METADATA_FILE}.")
        except Exception as e:
            app.logger.exception(f"Error inesperado guardando metadata: {e}")


# Instancia global del gestor de metadata
metadata_manager = MetadataManager()


class ChatManager:
    """Gestor de operaciones de chat."""

    @staticmethod
    def apply_context_limit(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Aplica límite de contexto a los mensajes."""
        if len(messages) <= config.MAX_CONTEXT_LENGTH:
            return messages

        system_message = [messages[0]] if messages and messages[0].get("role") == "system" else []
        user_assistant_msgs = [msg for msg in messages if msg.get("role") != "system"]
        msgs_to_keep = max(0, config.MAX_CONTEXT_LENGTH - len(system_message))
        limited_messages = system_message + user_assistant_msgs[-msgs_to_keep:]

        app.logger.debug(
            f"Contexto truncado de {len(messages)} a {len(limited_messages)} mensajes.")
        return limited_messages

    @staticmethod
    def ensure_system_message(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Asegura que los mensajes tengan el system prompt correcto."""
        if not messages or messages[0].get("role") != "system":
            return [config.DEFAULT_SYSTEM_MESSAGE.copy()] + (messages or [])
        
        if messages[0]['content'] != config.DEFAULT_SYSTEM_MESSAGE['content']:
            messages[0]['content'] = config.DEFAULT_SYSTEM_MESSAGE['content']
        
        return messages

    @staticmethod
    def get_chat_file_path(chat_id: str) -> str:
        """Retorna la ruta del archivo de chat."""
        return os.path.join(config.CHATS_DIR, f"{chat_id}.json")

    @classmethod
    def load_messages(cls, chat_id: str) -> Optional[List[Dict[str, str]]]:
        """Carga mensajes de un chat desde archivo."""
        FileManager.ensure_directory_exists(config.CHATS_DIR)
        chat_file = cls.get_chat_file_path(chat_id)

        messages = FileManager.read_json_file(chat_file)
        
        if messages is None:
            app.logger.warning(f"Archivo de chat no encontrado: {chat_file}")
            return None

        if not isinstance(messages, list):
            app.logger.error(f"Chat {chat_file} con formato inválido (no es lista).")
            return None
        
        if not messages:
            app.logger.warning(f"Chat {chat_file} vacío, inicializando con system message.")
            return [config.DEFAULT_SYSTEM_MESSAGE.copy()]
        
        # Validar que todos los elementos sean diccionarios con 'role' y 'content'
        if not all(isinstance(m, dict) and 'role' in m and 'content' in m for m in messages):
            app.logger.error(f"Chat {chat_file} contiene mensajes con formato inválido.")
            return None

        messages = cls.ensure_system_message(messages)
        messages = cls.apply_context_limit(messages)

        app.logger.debug(
            f"Chat {chat_id} cargado ({len(messages)} msgs después de aplicar contexto).")
        return messages

    @classmethod
    def save_messages(cls, chat_id: str, messages: List[Dict[str, str]]) -> bool:
        """Guarda mensajes de un chat en archivo."""
        FileManager.ensure_directory_exists(config.CHATS_DIR)
        chat_file = cls.get_chat_file_path(chat_id)

        messages = cls.ensure_system_message(messages)
        messages_to_save = cls.apply_context_limit(messages)

        if FileManager.write_json_file(chat_file, messages_to_save):
            app.logger.debug(f"Chat {chat_id} guardado ({len(messages_to_save)} msgs).")
            return True
        
        app.logger.error(f"Error guardando chat {chat_id}")
        return False


chat_manager = ChatManager()


def validate_chat_id(chat_id: str) -> bool:
    """Valida que chat_id sea un UUID válido."""
    try:
        uuid.UUID(chat_id)
        return True
    except (ValueError, AttributeError):
        return False


class OpenAIService:
    """Servicio para interactuar con la API de OpenAI."""

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

    @classmethod
    def get_api_parameters(cls, purpose: str) -> Dict[str, Any]:
        """Devuelve los parámetros específicos para cada tipo de llamada a la API."""
        return cls.API_PARAMETERS.get(purpose, cls.API_PARAMETERS["chat"])

    @classmethod
    def call_api(cls, messages: List[Dict[str, str]], model: str, purpose: str = "chat") -> Optional[str]:
        """Llama a la API de Chat Completions de OpenAI."""
        if not client:
            app.logger.error(f"Cliente OpenAI no inicializado ({purpose}).")
            return None

        try:
            app.logger.debug(
                f"Enviando {len(messages)} mensajes a OpenAI ({purpose}, modelo: {model})")

            params = {
                "model": model,
                "messages": messages,
                **cls.get_api_parameters(purpose)
            }

            response = client.chat.completions.create(**params)

            if not (response.choices and response.choices[0].message and 
                    response.choices[0].message.content):
                app.logger.error(f"Respuesta inválida de OpenAI ({purpose}, {model})")
                return None

            reply = response.choices[0].message.content.strip()
            app.logger.debug(f"Respuesta recibida ({purpose}): '{reply[:100]}...'")
            return reply

        except APIError as e:
            app.logger.error(f"Error API OpenAI ({purpose}, {model}): {str(e)}")
            return None
        except Exception as e:
            app.logger.exception(f"Error inesperado en OpenAI API ({purpose}): {e}")
            return None

    @classmethod
    def generate_title(cls, messages: List[Dict[str, str]]) -> Optional[str]:
        """Genera un título para la conversación usando la IA."""
        relevant_messages = [
            msg for msg in messages if msg["role"] in ["user", "assistant"]][-6:]
        
        if not relevant_messages:
            app.logger.warning("No hay mensajes relevantes para generar título.")
            return None

        title_prompt = [
            {"role": "system", "content": "Eres un experto en resumir conversaciones concisamente."},
            *relevant_messages,
            {"role": "user", 
             "content": f"Genera un título muy corto y descriptivo (máx ~5 palabras, "
                       f"{config.MAX_TITLE_LENGTH} chars) para esta conversación. "
                       f"Responde SOLO con el título."}
        ]

        generated_title = cls.call_api(title_prompt, config.OPENAI_TITLE_MODEL, purpose="title")
        
        if not generated_title:
            app.logger.error("Fallo al generar título.")
            return None

        # Limpiar y validar título
        cleaned_title = generated_title.replace('"', '').strip()[:config.MAX_TITLE_LENGTH]
        
        if len(cleaned_title) > 3 and not cleaned_title.lower().startswith("conversación sobre"):
            app.logger.info(f"Título generado: '{cleaned_title}'")
            return cleaned_title
        
        app.logger.warning(f"Título rechazado: '{cleaned_title}' (genérico/corto)")
        return None

    @classmethod
    def update_title_if_needed(cls, chat_id: str, messages: List[Dict[str, str]], 
                              metadata: Dict[str, Dict[str, Any]]) -> Optional[str]:
        """Verifica y genera título si es necesario."""
        if chat_id not in metadata:
            app.logger.warning(f"Metadata no encontrada para {chat_id}")
            return None

        current_title = metadata[chat_id].get("title")
        message_count = len([m for m in messages if m["role"] != "system"])
        min_messages = config.TITLE_GENERATION_MIN_MESSAGES - 1

        if current_title == "Nuevo Chat" and message_count >= min_messages:
            app.logger.info(f"Generando título para chat {chat_id}...")
            new_title = cls.generate_title(messages)
            
            if new_title:
                metadata[chat_id]["title"] = new_title
                return new_title
            
            app.logger.warning(f"Fallo al generar título para {chat_id}")
        
        return None


openai_service = OpenAIService()

# Rutas


@app.route("/")
def home() -> Any:
    try:
        return render_template("index.html")
    except Exception as e:  # pylint: disable=broad-except
        app.logger.exception(f"Error renderizando index.html: {e}")
        return "Error UI.", 500


@app.route("/new_chat", methods=["POST"])
def new_chat() -> Tuple[Any, int]:
    """Crea un nuevo chat."""
    try:
        chat_id = str(uuid.uuid4())
        messages = [config.DEFAULT_SYSTEM_MESSAGE.copy()]
        
        chat_manager.save_messages(chat_id, messages)
        
        metadata = metadata_manager.load()
        now_iso = datetime.now(timezone.utc).isoformat()
        metadata[chat_id] = {
            "id": chat_id, 
            "title": "Nuevo Chat",
            "created_at": now_iso, 
            "last_updated": now_iso
        }
        metadata_manager.save(metadata)
        
        app.logger.info(f"Nuevo chat creado: {chat_id}")
        return jsonify({
            "chat_id": chat_id, 
            "messages": messages, 
            "title": "Nuevo Chat"
        }), 201
    except Exception as e:
        app.logger.exception(f"Error creando chat: {e}")
        return jsonify({"error": "No se pudo crear el chat."}), 500


@app.route("/history", methods=["GET"])
def get_history() -> Tuple[Any, int]:
    """Obtiene el historial de chats."""
    try:
        metadata = metadata_manager.load()
        history_list = sorted(
            metadata.values(), 
            key=lambda i: i.get("last_updated", ""), 
            reverse=True
        )
        app.logger.debug(f"Historial solicitado: {len(history_list)} chats")
        return jsonify({"history": history_list}), 200
    except Exception as e:
        app.logger.exception(f"Error obteniendo historial: {e}")
        return jsonify({"error": "Error al obtener historial."}), 500


@app.route("/chat/<chat_id>", methods=["GET"])
def load_specific_chat(chat_id: str) -> Tuple[Any, int]:
    """Carga un chat específico."""
    app.logger.debug(f"GET /chat/{chat_id}")
    
    if not validate_chat_id(chat_id):
        app.logger.warning(f"Chat ID inválido rechazado: {chat_id}")
        abort(400, description="Chat ID inválido. Debe ser un UUID válido.")
    
    messages = chat_manager.load_messages(chat_id)
    if messages is None:
        abort(404, description=f"Chat no encontrado: {chat_id}")
    
    metadata = metadata_manager.load()
    chat_info = metadata.get(chat_id)
    chat_title = (
        chat_info.get("title", f"Chat {chat_id[:8]}...") 
        if chat_info 
        else f"Recuperado {chat_id[:8]}..."
    )
    
    app.logger.debug(f"Chat {chat_id} cargado. Título: {chat_title}")
    return jsonify({
        "chat_id": chat_id, 
        "messages": messages, 
        "title": chat_title
    }), 200


@app.route("/chat/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id: str) -> Tuple[Any, int]:
    """Elimina un chat."""
    app.logger.info(f"DELETE /chat/{chat_id}")
    
    if not validate_chat_id(chat_id):
        app.logger.warning(f"Chat ID inválido rechazado: {chat_id}")
        abort(400, description="Chat ID inválido. Debe ser un UUID válido.")
    
    chat_file = chat_manager.get_chat_file_path(chat_id)
    metadata = metadata_manager.load()
    
    metadata_deleted = False
    file_deleted = False
    
    # Eliminar metadata
    if chat_id in metadata:
        del metadata[chat_id]
        metadata_manager.save(metadata)
        metadata_deleted = True
        app.logger.info(f"Metadata eliminada: {chat_id}")
    
    # Eliminar archivo
    if os.path.exists(chat_file):
        try:
            os.remove(chat_file)
            file_deleted = True
            app.logger.info(f"Archivo eliminado: {chat_file}")
        except (OSError, PermissionError) as e:
            app.logger.error(f"Error eliminando archivo {chat_file}: {e}")
            return jsonify({"error": "Error eliminando archivo."}), 500
    
    if metadata_deleted or file_deleted:
        return jsonify({"message": f"Chat {chat_id} eliminado."}), 200
    
    abort(404, description=f"Chat no encontrado: {chat_id}")


@app.route("/chat/<chat_id>", methods=["POST"])
def process_chat_message(chat_id: str) -> Tuple[Any, int]:
    """Procesa un mensaje de usuario, llama a la IA, y maneja títulos."""
    app.logger.debug(f"POST /chat/{chat_id}")

    if not validate_chat_id(chat_id):
        app.logger.warning(f"Chat ID inválido rechazado: {chat_id}")
        abort(400, description="Chat ID inválido. Debe ser un UUID válido.")

    if not client:
        app.logger.error(f"Cliente OpenAI no configurado (chat: {chat_id})")
        return jsonify({"error": "Servicio AI no configurado."}), 503

    messages = chat_manager.load_messages(chat_id)
    if messages is None:
        app.logger.warning(f"Chat inexistente o corrupto: {chat_id}")
        abort(404, description=f"Chat no encontrado: {chat_id}")

    # Validar datos de entrada
    try:
        data = request.get_json(force=True)
    except Exception as e:
        app.logger.warning(f"JSON inválido en request (chat: {chat_id}): {e}")
        return jsonify({"error": "Formato JSON inválido."}), 400
    
    if not data or "mensaje" not in data:
        app.logger.warning(f"Falta campo 'mensaje' (chat: {chat_id})")
        return jsonify({"error": "Falta campo 'mensaje'."}), 400

    
    try:
        user_input = data["mensaje"].strip()
    except (KeyError, AttributeError, TypeError) as e:
        app.logger.warning(f"Campo 'mensaje' inválido (chat: {chat_id}): {e}")
        return jsonify({"error": "Campo 'mensaje' inválido."}), 400
    
    if not user_input:
        app.logger.warning(f"Mensaje vacío (chat: {chat_id})")
        return jsonify({"error": "Mensaje vacío."}), 400

    modelo_seleccionado = config.validate_model(
        data.get("modelo", config.OPENAI_CHAT_MODEL))
    app.logger.info(f"Procesando mensaje (chat: {chat_id}, modelo: {modelo_seleccionado})")

    # Agregar mensaje del usuario
    messages.append({"role": "user", "content": user_input})
    messages_for_api = chat_manager.apply_context_limit(messages)

    # Llamar a OpenAI
    assistant_reply = openai_service.call_api(
        messages_for_api,
        modelo_seleccionado,
        purpose="chat"
    )

    if assistant_reply is None:
        app.logger.error(f"Llamada API fallida (chat: {chat_id})")
        return jsonify({"error": "Error contactando asistente AI."}), 503

    # Guardar respuesta
    messages.append({"role": "assistant", "content": assistant_reply})
    
    # Actualizar metadata y título
    metadata = metadata_manager.load()
    new_title = openai_service.update_title_if_needed(chat_id, messages, metadata)

    now_iso = datetime.now(timezone.utc).isoformat()
    if chat_id in metadata:
        metadata[chat_id]["last_updated"] = now_iso
        if new_title:
            metadata[chat_id]["title"] = new_title
    else:
        app.logger.warning(f"Creando metadata faltante para {chat_id}")
        metadata[chat_id] = {
            "id": chat_id,
            "title": new_title or "Chat Recuperado",
            "created_at": now_iso,
            "last_updated": now_iso
        }

    metadata_manager.save(metadata)
    
    if not chat_manager.save_messages(chat_id, messages):
        app.logger.error(f"Error guardando mensajes después de respuesta (chat: {chat_id})")
        # Aún devolvemos la respuesta al usuario, pero loggeamos el error

    app.logger.info(f"Respuesta enviada (chat: {chat_id}, modelo: {modelo_seleccionado})")
    return jsonify({
        "respuesta": assistant_reply,
        "timestamp": now_iso,
        "new_title": metadata.get(chat_id, {}).get("title")
    }), 200

# Manejadores de errores


@app.errorhandler(400)
def bad_request_error(error: Exception) -> Tuple[Any, int]:
    description = getattr(error, 'description', 'Solicitud inválida.')
    app.logger.warning(f"Error 400: {request.path} - {description}")
    return jsonify(error=description), 400


@app.errorhandler(404)
def not_found_error(error: Exception) -> Tuple[Any, int]:
    description = getattr(error, 'description', 'Recurso no encontrado.')
    app.logger.warning(f"Error 404: {request.path} - {description}")
    return jsonify(error=description), 404


@app.errorhandler(500)
def internal_error(error: Exception) -> Tuple[Any, int]:
    app.logger.exception(f"Error 500 Interno: {error}")
    return jsonify(error="Ocurrió un error interno en el servidor."), 500


@app.errorhandler(503)
def service_unavailable_error(error: Exception) -> Tuple[Any, int]:
    description = getattr(error, 'description', 'Servicio no disponible.')
    app.logger.error(f"Error 503: {request.path} - {description}")
    return jsonify(error=description), 503


@app.errorhandler(Exception)
def handle_generic_exception(error: Exception) -> Tuple[Any, int]:  # pylint: disable=broad-except
    app.logger.exception(
        f"Excepción no manejada capturada globalmente: {error}")
    return jsonify(error="Ocurrió un error inesperado."), 500


def print_startup_banner() -> None:
    """Imprime el banner de inicio del servidor."""
    print("\n" + "="*60)
    print(" Synapse AI Server")
    print("="*60)
    print(f" Modo Debug Flask: {config.FLASK_DEBUG}")
    print(f" Nivel de Log: {config.LOG_LEVEL}")
    print(f" Orígenes CORS: {config.CORS_ORIGINS}")
    print(" URL Local: http://127.0.0.1:5000")
    print("\nIniciando servidor Flask...")


def main() -> None:
    """Función principal de inicialización."""
    # Asegurar directorios existen
    try:
        FileManager.ensure_directory_exists(config.CHATS_DIR)
    except OSError as e:
        app.logger.critical(f"Error crítico creando directorios: {e}")
        sys.exit(1)

    # Advertencia si no hay API key
    if not config.OPENAI_API_KEY:
        print("\n" + "="*60, file=sys.stderr)
        print(" ADVERTENCIA: OPENAI_APIKEY no configurada", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)

    print_startup_banner()

    # Iniciar servidor
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=config.FLASK_DEBUG,
        threaded=True,
        use_reloader=config.FLASK_DEBUG
    )


if __name__ == "__main__":
    main()
