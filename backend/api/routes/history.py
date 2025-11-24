"""History routes blueprint."""
from flask import Blueprint, jsonify

from core.logging import get_logger
from schemas.chat import HistoryResponse, ChatMetadataResponse

logger = get_logger(__name__)

# Blueprint will be initialized with dependencies in create_app
history_bp = Blueprint('history', __name__, url_prefix='/api/v1/history')


def init_history_routes(chat_service):
    """Initialize history routes with dependencies.
    
    Args:
        chat_service: ChatService instance
    """
    
    @history_bp.route('', methods=['GET'])
    def get_history():
        """Get chat history.
        
        Returns:
            200: History retrieved successfully
            500: Server error
        """
        try:
            history_list = chat_service.get_history()
            
            response = HistoryResponse(
                history=[
                    ChatMetadataResponse(
                        id=meta.id,
                        title=meta.title,
                        created_at=meta.created_at,
                        last_updated=meta.last_updated
                    )
                    for meta in history_list
                ]
            )
            
            logger.debug(f"Historial solicitado: {len(history_list)} chats")
            return jsonify(response.model_dump()), 200
        
        except Exception as e:
            logger.exception(f"Error obteniendo historial: {e}")
            return jsonify(error="Error al obtener historial."), 500
