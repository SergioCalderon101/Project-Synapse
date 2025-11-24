"""Chat routes blueprint."""
from flask import Blueprint, jsonify, request, abort
from pydantic import ValidationError

from core.logging import get_logger
from schemas.chat import (
    SendMessageRequest,
    SendMessageResponse,
    CreateChatResponse,
    LoadChatResponse,
    DeleteChatResponse,
    MessageResponse
)
from utils.validators import validate_chat_id

logger = get_logger(__name__)

# Blueprint will be initialized with dependencies in create_app
chat_bp = Blueprint('chat', __name__, url_prefix='/api/v1/chat')


def init_chat_routes(chat_service):
    """Initialize chat routes with dependencies.
    
    Args:
        chat_service: ChatService instance
    """
    
    @chat_bp.route('', methods=['POST'])
    def create_chat():
        """Create a new chat.
        
        Returns:
            201: Chat created successfully
            500: Server error
        """
        try:
            chat_id, messages, title = chat_service.create_chat()
            
            response = CreateChatResponse(
                chat_id=chat_id,
                messages=[
                    MessageResponse(role=msg.role, content=msg.content)
                    for msg in messages
                ],
                title=title
            )
            
            return jsonify(response.model_dump()), 201
        
        except Exception as e:
            logger.exception(f"Error creando chat: {e}")
            return jsonify(error="No se pudo crear el chat."), 500
    
    @chat_bp.route('/<chat_id>', methods=['GET'])
    def load_chat(chat_id: str):
        """Load a specific chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            200: Chat loaded successfully
            400: Invalid chat ID
            404: Chat not found
        """
        logger.debug(f"GET /api/v1/chat/{chat_id}")
        
        if not validate_chat_id(chat_id):
            logger.warning(f"Chat ID inválido rechazado: {chat_id}")
            abort(400, description="Chat ID inválido. Debe ser un UUID válido.")
        
        chat = chat_service.get_chat(chat_id)
        if chat is None:
            abort(404, description=f"Chat no encontrado: {chat_id}")
        
        response = LoadChatResponse(
            chat_id=chat.chat_id,
            messages=[
                MessageResponse(role=msg.role, content=msg.content)
                for msg in chat.messages
            ],
            title=chat.title or f"Chat {chat_id[:8]}..."
        )
        
        logger.debug(f"Chat {chat_id} cargado. Título: {response.title}")
        return jsonify(response.model_dump()), 200
    
    @chat_bp.route('/<chat_id>', methods=['DELETE'])
    def delete_chat(chat_id: str):
        """Delete a chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            200: Chat deleted successfully
            400: Invalid chat ID
            404: Chat not found
        """
        logger.info(f"DELETE /api/v1/chat/{chat_id}")
        
        if not validate_chat_id(chat_id):
            logger.warning(f"Chat ID inválido rechazado: {chat_id}")
            abort(400, description="Chat ID inválido. Debe ser un UUID válido.")
        
        deleted = chat_service.delete_chat(chat_id)
        if not deleted:
            abort(404, description=f"Chat no encontrado: {chat_id}")
        
        response = DeleteChatResponse(message=f"Chat {chat_id} eliminado.")
        return jsonify(response.model_dump()), 200
    
    @chat_bp.route('/<chat_id>', methods=['POST'])
    def send_message(chat_id: str):
        """Send a message to a chat.
        
        Args:
            chat_id: Chat UUID
            
        Returns:
            200: Message processed successfully
            400: Invalid request
            404: Chat not found
            503: AI service unavailable
        """
        logger.debug(f"POST /api/v1/chat/{chat_id}")
        
        if not validate_chat_id(chat_id):
            logger.warning(f"Chat ID inválido rechazado: {chat_id}")
            abort(400, description="Chat ID inválido. Debe ser un UUID válido.")
        
        # Validate request
        try:
            data = request.get_json(force=True)
            req = SendMessageRequest(**data)
        except ValidationError as e:
            errors = e.errors()
            if errors:
                message = errors[0].get('msg', 'Error de validación.')
            else:
                message = 'Error de validación.'
            return jsonify(error=message), 400
        except Exception as e:
            logger.warning(f"JSON inválido en request (chat: {chat_id}): {e}")
            return jsonify(error="Formato JSON inválido."), 400
        
        # Process message
        response_text, timestamp, new_title = chat_service.process_message(
            chat_id=chat_id,
            user_message=req.mensaje,
            model=req.modelo or None
        )
        
        if response_text is None:
            return jsonify(error="Error contactando asistente AI."), 503
        
        response = SendMessageResponse(
            respuesta=response_text,
            timestamp=timestamp,
            new_title=new_title
        )
        
        return jsonify(response.model_dump()), 200
