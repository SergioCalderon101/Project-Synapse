# --- app.py (v6.0 - Chat AI sin funcionalidad PDF) ---
import os
import json
import uuid
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from flask import Flask, request, jsonify, render_template, send_from_directory, abort
from flask_cors import CORS
from openai import OpenAI, APIError
from dotenv import load_dotenv
from filelock import FileLock

# --- 1. Configuración Centralizada ---
load_dotenv()


class Config:
    """Clase para centralizar la configuración de la aplicación."""
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_APIKEY")

    # Modelos soportados por la app
    SUPPORTED_OPENAI_MODELS = [
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4",
        "gpt-4o-mini"  
    ]

    # Modelo por defecto
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
    OPENAI_TITLE_MODEL: str = os.getenv("OPENAI_TITLE_MODEL", "gpt-3.5-turbo")

    # Directorios
    CHATS_DIR: str = "chats"
    METADATA_FILE: str = os.path.join(CHATS_DIR, "chats_metadata.json")
    METADATA_LOCK_FILE: str = os.path.join(CHATS_DIR, "metadata.lock")
    STATIC_FOLDER: str = "static"
    TEMPLATES_FOLDER: str = "templates"
    LOGS_FOLDER: str = "logs"
    LOG_FILE: str = os.path.join(LOGS_FOLDER, "app.log")

    # Configuración de logging y servidor
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    # Configuración del chat
    MAX_TITLE_LENGTH: int = 40
    MAX_CONTEXT_LENGTH: int = 12
    TITLE_GENERATION_MIN_MESSAGES: int = 5

    @classmethod
    def validate_model(cls, model: str) -> str:
        """Valida que el modelo esté soportado."""
        if model not in cls.SUPPORTED_OPENAI_MODELS:
            return cls.OPENAI_CHAT_MODEL
        return model

    # Mensaje por defecto del sistema
    DEFAULT_SYSTEM_MESSAGE: Dict[str, str] = {
        "role": "system",
        "content": """Eres Synapse AI, un asistente inteligente, adaptable y profesional. Tu propósito es proporcionar ayuda útil, precisa y contextualmente apropiada a cada usuario.\n\n## Principios Fundamentales\n\n**Análisis Inteligente:**\n- Evalúa cada consulta en su contexto completo\n- Identifica la intención real del usuario más allá de las palabras exactas\n- Adapta tu enfoque según la complejidad y naturaleza de la solicitud\n- Para problemas complejos, descompón en pasos lógicos cuando sea útil\n\n**Comunicación Efectiva:**\n- Sé directo y conciso, pero completo\n- Estructura tu respuesta de manera clara y lógica\n- Usa formato Markdown apropiadamente para mejorar la legibilidad\n- Adapta tu tono al contexto (técnico, casual, formal según corresponda)\n- Evita redundancias y información innecesaria\n\n**Gestión de Contexto:**\n- Mantén coherencia con el historial de conversación\n- Construye sobre intercambios anteriores de manera inteligente\n- Pide clarificaciones solo cuando realmente agreguen valor\n- Recuerda preferencias y patrones del usuario cuando sea relevante\n\n**Manejo de Contenido:**\n- Genera contenido completo y bien estructurado en tu respuesta\n- Organiza información compleja usando encabezados, listas y formatos apropiados\n- Proporciona ejemplos prácticos cuando sea útil\n- Incluye consideraciones importantes o limitaciones cuando sea relevante\n\n**Resolución de Problemas:**\n- Si una solicitud es ambigua, ofrece la interpretación más probable y menciona alternativas si es necesario\n- Para errores o problemas técnicos, proporciona diagnóstico y soluciones paso a paso\n- Adapta el nivel de detalle técnico al conocimiento aparente del usuario\n- Sugiere mejores prácticas cuando sea apropiado\n\n**Calidad y Precisión:**\n- Prioriza respuestas precisas sobre respuestas rápidas\n- Reconoce abiertamente las limitaciones de tu conocimiento\n- Para información que cambia frecuentemente, sugiere verificación cuando sea apropiado\n- Mantén objetividad, especialmente en temas controvertidos\n\n## Comportamientos Adaptativos\n\n- **Consultas técnicas:** Proporciona detalles técnicos precisos, código limpio, y explica conceptos complejos\n- **Solicitudes creativas:** Ofrece ideas originales y bien desarrolladas\n- **Problemas de análisis:** Presenta razonamiento estructurado y considera múltiples perspectivas\n- **Tareas de escritura:** Crea contenido apropiado para el propósito y audiencia especificados\n\nTu objetivo es ser genuinamente útil adaptándote inteligentemente a las necesidades específicas de cada interacción."""
    }


config = Config()

# --- 2. Inicialización de Flask, CORS y Logging  ---
app = Flask(__name__, template_folder=config.TEMPLATES_FOLDER,
            static_folder=config.STATIC_FOLDER)
cors_origins = config.CORS_ORIGINS.split(
    ',') if config.CORS_ORIGINS != "*" else "*"
CORS(app, origins=cors_origins, supports_credentials=True)

if not os.path.exists(config.LOGS_FOLDER):
    try:
        os.makedirs(config.LOGS_FOLDER)
    except OSError as e:
        print(
            f"CRITICAL: No se pudo crear la carpeta de logs '{config.LOGS_FOLDER}': {e}", file=sys.stderr)
        sys.exit(1)

log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
try:
    file_handler = RotatingFileHandler(
        config.LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    app.logger.addHandler(file_handler)
except Exception as e:
    print(
        f"WARNING: No se pudo configurar el logging a archivo '{config.LOG_FILE}': {e}", file=sys.stderr)

app.logger.addHandler(stream_handler)
app.logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
app.logger.propagate = False

# --- 3. Cliente OpenAI ---
client: Optional[OpenAI] = None
if config.OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        app.logger.info(f"Cliente OpenAI inicializado.")
        app.logger.debug(
            f"Modelo Chat (Default): {config.OPENAI_CHAT_MODEL}, Modelo Título: {config.OPENAI_TITLE_MODEL}")
    except Exception as e:
        app.logger.exception(f"Error fatal inicializando OpenAI: {e}")
else:
    app.logger.warning(
        "OPENAI_APIKEY no encontrada en variables de entorno. Funcio|nalidad AI deshabilitada.")

# --- 4. Funciones Auxiliares (Chats, Metadatos con Locking) ---


def ensure_chats_dir_exists() -> None:
    if not os.path.exists(config.CHATS_DIR):
        try:
            os.makedirs(config.CHATS_DIR)
            app.logger.info(f"Carpeta de chats '{config.CHATS_DIR}' creada.")
        except OSError as e:
            app.logger.error(
                f"Error crítico: No se pudo crear '{config.CHATS_DIR}': {e}")
            raise


def load_metadata() -> Dict[str, Dict[str, Any]]:
    ensure_chats_dir_exists()
    lock = FileLock(config.METADATA_LOCK_FILE)
    metadata = {}
    try:
        with lock.acquire(timeout=5):
            if os.path.exists(config.METADATA_FILE):
                try:
                    with open(config.METADATA_FILE, "r", encoding="utf-8") as f:
                        loaded_data = json.load(f)
                    if isinstance(loaded_data, dict):
                        metadata = loaded_data
                        # app.logger.debug(f"Metadatos cargados desde {config.METADATA_FILE}") # Reducir verbosidad
                    else:
                        app.logger.warning(
                            f"{config.METADATA_FILE} contiene datos inválidos. Reiniciando.")
                except (IOError, json.JSONDecodeError) as e:
                    app.logger.error(
                        f"Error cargando o parseando {config.METADATA_FILE}: {e}. Reiniciando metadatos.")
                except Exception as e:
                    app.logger.exception(
                        f"Error inesperado cargando metadatos: {e}")
    except TimeoutError:
        app.logger.error(
            f"Timeout esperando el lock para leer {config.METADATA_FILE}.")
    except Exception as e:
        app.logger.exception(
            f"Error adquiriendo lock o durante lectura de metadatos: {e}")
    return metadata


def save_metadata(metadata: Dict[str, Dict[str, Any]]) -> None:
    ensure_chats_dir_exists()
    lock = FileLock(config.METADATA_LOCK_FILE)
    try:
        with lock.acquire(timeout=5):
            try:
                with open(config.METADATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                app.logger.debug(
                    f"Metadatos guardados en {config.METADATA_FILE} ({len(metadata)} chats)")
            except IOError as e:
                app.logger.error(
                    f"Error de I/O guardando metadatos en {config.METADATA_FILE}: {e}")
            except Exception as e:
                app.logger.exception(
                    f"Error inesperado guardando metadatos: {e}")
    except TimeoutError:
        app.logger.error(
            f"Timeout esperando el lock para guardar {config.METADATA_FILE}.")
    except Exception as e:
        app.logger.exception(
            f"Error adquiriendo lock o durante guardado de metadatos: {e}")


def _apply_context_limit(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if len(messages) > config.MAX_CONTEXT_LENGTH:
        system_message = [messages[0]] if messages and messages[0].get(
            "role") == "system" else []
        user_assistant_msgs = [
            msg for msg in messages if msg.get("role") != "system"]
        msgs_to_keep = config.MAX_CONTEXT_LENGTH - len(system_message)
        if msgs_to_keep < 0:
            msgs_to_keep = 0
        limited_messages = system_message + user_assistant_msgs[-msgs_to_keep:]
        app.logger.debug(
            f"Contexto truncado de {len(messages)} a {len(limited_messages)} mensajes.")
        return limited_messages
    return messages


def load_chat_messages(chat_id: str) -> Optional[List[Dict[str, str]]]:
    ensure_chats_dir_exists()
    chat_file = os.path.join(config.CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(chat_file):
        app.logger.warning(f"Archivo de chat no encontrado: {chat_file}")
        return None
    try:
        with open(chat_file, "r", encoding="utf-8") as f:
            messages = json.load(f)
        if not isinstance(messages, list) or not messages:
            app.logger.warning(
                f"Chat {chat_file} vacío o con formato inválido. Recreando.")
            return [config.DEFAULT_SYSTEM_MESSAGE.copy()]
        if messages[0].get("role") != "system":
            app.logger.warning(
                f"Chat {chat_id} no comenzaba con system prompt. Añadiéndolo.")
            messages.insert(0, config.DEFAULT_SYSTEM_MESSAGE.copy())
        else:
            # Siempre actualizar por si cambia
            messages[0]['content'] = config.DEFAULT_SYSTEM_MESSAGE['content']
        messages = _apply_context_limit(messages)
        app.logger.debug(
            f"Chat {chat_id} cargado ({len(messages)} msgs después de aplicar contexto).")
        return messages
    except (IOError, json.JSONDecodeError) as e:
        app.logger.error(
            f"Error cargando o parseando chat {chat_id} desde {chat_file}: {e}")
        return None
    except Exception as e:
        app.logger.exception(f"Error inesperado cargando chat {chat_id}: {e}")
        return None


def save_chat_messages(chat_id: str, messages: List[Dict[str, str]]) -> None:
    ensure_chats_dir_exists()
    chat_file = os.path.join(config.CHATS_DIR, f"{chat_id}.json")
    if not messages or messages[0].get("role") != "system":
        messages = [config.DEFAULT_SYSTEM_MESSAGE.copy()] + (messages or [])
    else:
        messages[0]['content'] = config.DEFAULT_SYSTEM_MESSAGE['content']
    messages_to_save = _apply_context_limit(messages)
    try:
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump(messages_to_save, f, ensure_ascii=False, indent=2)
        app.logger.debug(
            f"Chat {chat_id} guardado en {chat_file} ({len(messages_to_save)} msgs).")
    except IOError as e:
        app.logger.error(f"Error guardando chat {chat_id} en {chat_file}: {e}")
    except Exception as e:
        app.logger.exception(f"Error inesperado guardando chat {chat_id}: {e}")

# --- 5. Funciones Auxiliares Específicas ---


def _get_api_parameters(purpose: str) -> Dict[str, Any]:
    """Devuelve los parámetros específicos para cada tipo de llamada a la API."""
    base_params = {"temperature": 0.6, "max_tokens": 2000, "top_p": 0.9}

    if purpose == "chat":
        return {**base_params, "frequency_penalty": 0.1, "presence_penalty": 0.1}
    elif purpose == "title":
        return {"temperature": 0.3, "max_tokens": 20, "n": 1, "stop": None}

    return base_params


def _call_openai_api(messages_for_api: List[Dict[str, str]], model_to_use: str, purpose: str = "chat") -> Optional[str]:
    """Llama a la API de Chat Completions de OpenAI usando el modelo especificado."""
    if not client:
        app.logger.error(
            f"Intento de llamar a OpenAI API ({purpose}) sin cliente inicializado.")
        return None

    try:
        app.logger.debug(
            f"Enviando {len(messages_for_api)} mensajes a OpenAI API ({purpose}, modelo: {model_to_use})...")

        params = {
            "model": model_to_use,
            "messages": messages_for_api,
            **_get_api_parameters(purpose)
        }

        response = client.chat.completions.create(**params)

        if response.choices and response.choices[0].message and response.choices[0].message.content:
            reply = response.choices[0].message.content.strip()
            app.logger.debug(
                f"Respuesta recibida de OpenAI API ({purpose}): '{reply[:100]}...'")
            return reply
        else:
            app.logger.error(
                f"Respuesta inválida/vacía de OpenAI API ({purpose}, modelo: {model_to_use})")
            return None

    except APIError as e:
        app.logger.error(
            f"Error de API OpenAI ({purpose}, modelo: {model_to_use}): {e.status_code} - {e.message}")
        return None
    except Exception as e:
        app.logger.exception(
            f"Error inesperado en llamada a OpenAI API ({purpose}, modelo: {model_to_use}): {e}")
        return None


def _generate_chat_title(messages: List[Dict[str, str]]) -> Optional[str]:
    """Genera un título para la conversación usando la IA."""
    relevant_messages = [
        msg for msg in messages if msg["role"] in ["user", "assistant"]][-6:]
    if not relevant_messages:
        app.logger.warning(
            "No hay mensajes U/A relevantes para generar título.")
        return None
    title_prompt_messages = [
        {"role": "system", "content": "Eres un experto en resumir conversaciones concisamente."},
        *relevant_messages,
        {"role": "user",
            "content": f"Genera un título muy corto y descriptivo (máx ~5 palabras, {config.MAX_TITLE_LENGTH} chars) para esta conversación... Responde SOLO con el título..."}
    ]
    generated_title = _call_openai_api(
        title_prompt_messages, config.OPENAI_TITLE_MODEL, purpose="title")
    if generated_title:
        generated_title = generated_title.replace(
            '"', '').strip()[:config.MAX_TITLE_LENGTH]
        if len(generated_title) > 3 and not generated_title.lower().startswith("conversación sobre"):
            app.logger.info(
                f"Título generado por IA validado: '{generated_title}'")
            return generated_title
        else:
            app.logger.warning(
                f"Título IA ('{generated_title}') descartado (vacío/genérico/corto).")
            return None
    else:
        app.logger.error("La llamada a la API para generar título falló.")
        return None


def _update_chat_title_if_needed(chat_id: str, messages: List[Dict[str, str]], metadata: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """Verifica si se necesita generar un título y lo hace, actualizando metadata."""
    new_title_generated = None
    if chat_id not in metadata:
        app.logger.warning(
            f"Metadata no encontrada para {chat_id} al verificar/generar título.")
        return None
    current_title = metadata[chat_id].get("title")
    message_count = len([m for m in messages if m["role"] != "system"])
    min_ua_messages_for_title = config.TITLE_GENERATION_MIN_MESSAGES - 1
    if current_title == "Nuevo Chat" and message_count >= min_ua_messages_for_title:
        app.logger.info(f"Intentando generar título para chat {chat_id}...")
        new_title = _generate_chat_title(messages)
        if new_title:
            app.logger.info(
                f"Título generado. Actualizando metadata para {chat_id}: '{new_title}'")
            # Actualizar el dict de metadata directamente
            metadata[chat_id]["title"] = new_title
            new_title_generated = new_title
        else:
            app.logger.warning(f"Generación de título para {chat_id} falló.")
    # else: # No es necesario loguear si no se cumplen condiciones
    #      app.logger.debug(f"No se generan títulos para {chat_id}...")
    return new_title_generated

# --- 6. Rutas Flask ---


@app.route("/")
def home() -> Any:
    try:
        return render_template("index.html")
    except Exception as e:
        app.logger.exception(f"Error renderizando index.html: {e}")
        return "Error UI.", 500


@app.route("/new_chat", methods=["POST"])
def new_chat() -> Tuple[Any, int]:
    try:
        chat_id = str(uuid.uuid4())
        messages = [config.DEFAULT_SYSTEM_MESSAGE.copy()]
        save_chat_messages(chat_id, messages)  # Guarda archivo inicial
        metadata = load_metadata()
        now_iso = datetime.now(timezone.utc).isoformat()
        metadata[chat_id] = {"id": chat_id, "title": "Nuevo Chat",
                             "created_at": now_iso, "last_updated": now_iso}
        save_metadata(metadata)  # Guarda metadata actualizada
        app.logger.info(f"Nuevo chat creado con ID: {chat_id}")
        return jsonify({"chat_id": chat_id, "messages": messages, "title": "Nuevo Chat"}), 201
    except Exception as e:
        app.logger.exception(f"Error creando chat: {e}")
        return jsonify({"error": "No se pudo crear."}), 500


@app.route("/history", methods=["GET"])
def get_history() -> Tuple[Any, int]:
    try:
        metadata = load_metadata()
        history_list = sorted(metadata.values(), key=lambda i: i.get(
            "last_updated", ""), reverse=True)
        app.logger.debug(f"Historial solicitado. {len(history_list)} chats.")
        return jsonify({"history": history_list}), 200
    except Exception as e:
        app.logger.exception(f"Error historial: {e}")
        return jsonify({"error": "Error historial."}), 500


@app.route("/chat/<chat_id>", methods=["GET"])
def load_specific_chat(chat_id: str) -> Tuple[Any, int]:
    app.logger.debug(f"GET /chat/{chat_id}")
    messages = load_chat_messages(chat_id)
    if messages is None:
        abort(404, description=f"Chat no encontrado: {chat_id}.")
    metadata = load_metadata()
    chat_info = metadata.get(chat_id)
    chat_title = chat_info.get(
        "title", f"Chat {chat_id[:8]}...") if chat_info else f"Recuperado {chat_id[:8]}..."
    app.logger.debug(f"Chat {chat_id} cargado. Título: {chat_title}")
    return jsonify({"chat_id": chat_id, "messages": messages, "title": chat_title}), 200


@app.route("/chat/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id: str) -> Tuple[Any, int]:
    app.logger.info(f"DELETE /chat/{chat_id}")
    chat_file = os.path.join(config.CHATS_DIR, f"{chat_id}.json")
    metadata = load_metadata()
    metadata_deleted, file_deleted = False, False
    if chat_id in metadata:
        del metadata[chat_id]
        save_metadata(metadata)
        metadata_deleted = True
        app.logger.info(f"Metadata eliminada: {chat_id}")
    if os.path.exists(chat_file):
        try:
            os.remove(chat_file)
            file_deleted = True
            app.logger.info(f"Archivo eliminado: {chat_file}")
        except Exception as e:
            app.logger.error(f"Error eliminando {chat_file}: {e}")
            return jsonify({"error": "Error eliminando archivo."}), 500
    if metadata_deleted or file_deleted:
        return jsonify({"message": f"Chat {chat_id} eliminado."}), 200
    else:
        abort(404, description=f"Chat no encontrado: {chat_id}.")


@app.route("/static/<path:filename>")
def static_files(filename: str) -> Any:
    try:
        return send_from_directory(app.static_folder, filename)
    except FileNotFoundError:
        abort(404, description=f"Archivo no hallado: {filename}.")
    except Exception as e:
        app.logger.exception(f"Error sirviendo {filename}:{e}")
        return jsonify({"error": "Error servidor."}), 500

# ---> AQUI CAMBIO: Ruta POST /chat/<chat_id> REEMPLAZADA <---


@app.route("/chat/<chat_id>", methods=["POST"])
def process_chat_message(chat_id: str) -> Tuple[Any, int]:
    """Procesa un mensaje de usuario, llama a la IA, y maneja títulos."""
    app.logger.debug(f"Solicitud POST recibida para chat ID: {chat_id}")

    if not client:
        app.logger.error(
            f"Procesamiento abortado ({chat_id}): Cliente OpenAI no configurado.")
        return jsonify({"error": "Servicio AI no configurado."}), 503

    messages = load_chat_messages(chat_id)
    if messages is None:
        app.logger.warning(f"POST a chat inexistente o con error: {chat_id}")
        abort(404, description=f"Chat no encontrado o corrupto: {chat_id}.")

    try:
        data = request.get_json()
        if not data or "mensaje" not in data:
            app.logger.warning(f"POST inválido ({chat_id}): Falta 'mensaje'.")
            return jsonify({"error": "Falta campo 'mensaje'."}), 400
        user_input = data["mensaje"].strip()
        if not user_input:
            app.logger.warning(f"POST inválido ({chat_id}): Mensaje vacío.")
            return jsonify({"error": "Mensaje vacío."}), 400

        modelo_seleccionado = config.validate_model(
            data.get("modelo", config.OPENAI_CHAT_MODEL))
        app.logger.info(
            f"Procesando mensaje para chat {chat_id} usando modelo: {modelo_seleccionado}")

    except Exception as e:
        app.logger.exception(
            f"Error procesando JSON de entrada para chat {chat_id}: {e}")
        return jsonify({"error": "Error procesando datos de entrada."}), 400

    # Añadir mensaje de usuario al historial
    messages.append({"role": "user", "content": user_input})

    # Procesar mensaje con la IA
    messages_for_api = _apply_context_limit(messages)
    assistant_reply_content = _call_openai_api(
        messages_for_api,
        modelo_seleccionado,
        purpose="chat"
    )

    if assistant_reply_content is None:
        app.logger.error(f"Llamada API fallida para chat {chat_id}")
        return jsonify({"error": "Error contactando asistente AI. Intenta de nuevo."}), 503

    final_assistant_reply = assistant_reply_content

    # Guardar respuesta del asistente
    messages.append({"role": "assistant", "content": final_assistant_reply})

    # Actualizar metadatos y título si es necesario
    metadata = load_metadata()
    new_title = _update_chat_title_if_needed(chat_id, messages, metadata)

    now_iso = datetime.now(timezone.utc).isoformat()
    if chat_id in metadata:
        metadata[chat_id]["last_updated"] = now_iso
        if new_title:
            metadata[chat_id]["title"] = new_title
    else:
        app.logger.warning(
            f"Creando metadata faltante para {chat_id} sobre la marcha.")
        metadata[chat_id] = {
            "id": chat_id, "title": (new_title or "Chat Recuperado"),
            "created_at": now_iso, "last_updated": now_iso
        }

    save_metadata(metadata)
    save_chat_messages(chat_id, messages)

    response_data = {
        "respuesta": final_assistant_reply,
        "timestamp": now_iso,
        "new_title": metadata.get(chat_id, {}).get("title")
    }
    app.logger.info(
        f"Respuesta enviada exitosamente para chat {chat_id} (Modelo: {modelo_seleccionado}).")
    return jsonify(response_data), 200

# --- 7. Manejadores de Errores ---


@app.errorhandler(404)
def not_found_error(error: Exception) -> Tuple[Any, int]:
    description = getattr(error, 'description', 'Recurso no encontrado.')
    app.logger.warning(f"Error 404: {request.path} - {description}")
    return jsonify(error=description), 404


@app.errorhandler(500)
def internal_error(error: Exception) -> Tuple[Any, int]:
    app.logger.exception(f"Error 500 Interno: {error}")
    return jsonify(error="Ocurrió un error interno en el servidor."), 500


@app.errorhandler(Exception)
def handle_generic_exception(error: Exception) -> Tuple[Any, int]:
    app.logger.exception(
        f"Excepción no manejada capturada globalmente: {error}")
    return jsonify(error="Ocurrió un error inesperado."), 500


# --- 8. Bloque de Ejecución (MODIFICADO para arrancar siempre) ---
if __name__ == "__main__":
    try:
        ensure_chats_dir_exists()
        if not os.path.exists(config.TEMPLATES_FOLDER):
            os.makedirs(config.TEMPLATES_FOLDER)
            app.logger.info(f"'{config.TEMPLATES_FOLDER}' creado.")
        if not os.path.exists(config.STATIC_FOLDER):
            os.makedirs(config.STATIC_FOLDER)
            app.logger.info(f"'{config.STATIC_FOLDER}' creado.")
        if not os.path.exists(config.LOGS_FOLDER):
            os.makedirs(config.LOGS_FOLDER)
            app.logger.info(f"'{config.LOGS_FOLDER}' creado.")
    except OSError as e:
        app.logger.critical(
            f"CRITICAL: No se pudo crear directorio '{e.filename}'. {e}")
        sys.exit(1)
    except Exception as e:
        app.logger.critical(f"CRITICAL: Error inicializando directorios: {e}")
        sys.exit(1)

    if not config.OPENAI_API_KEY:
        print("\n" + "="*60, file=sys.stderr)
        print(" ADVERTENCIA: OPENAI_APIKEY no configurada...", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)

    print("\n" + "="*60)
    print(" Synapse AI Server")  # Actualizar versión
    print("="*60)
    print(f" Modo Debug Flask: {config.FLASK_DEBUG}")
    print(f" Nivel de Log: {config.LOG_LEVEL}")
    print(f" Orígenes CORS: {config.CORS_ORIGINS}")
    print(f" URL: http://localhost:5000 (o http://<your-ip>:5000)")
    print("\nIniciando servidor Flask...")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=config.FLASK_DEBUG,
        threaded=True,
        use_reloader=config.FLASK_DEBUG  # Recargador solo si debug está activo
    )
# --- Fin del archivo ---
