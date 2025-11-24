"""Error handlers for API."""
from flask import jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from core.logging import get_logger

logger = get_logger(__name__)


def register_error_handlers(app):
    """Register error handlers for the Flask app.
    
    Args:
        app: Flask application
    """
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {error}")
        errors = error.errors()
        if errors:
            # Get first error message
            first_error = errors[0]
            message = first_error.get('msg', 'Error de validación.')
        else:
            message = 'Error de validación.'
        
        return jsonify(error=message), 400
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 errors."""
        description = getattr(error, 'description', 'Solicitud inválida.')
        logger.warning(f"Error 400: {error}")
        return jsonify(error=description), 400
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        description = getattr(error, 'description', 'Recurso no encontrado.')
        logger.warning(f"Error 404: {error}")
        return jsonify(error=description), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.exception(f"Error 500 Interno: {error}")
        return jsonify(error="Ocurrió un error interno en el servidor."), 500
    
    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Handle 503 errors."""
        description = getattr(error, 'description', 'Servicio no disponible.')
        logger.error(f"Error 503: {error}")
        return jsonify(error=description), 503
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all HTTP exceptions."""
        logger.warning(f"HTTP Exception: {error}")
        return jsonify(error=error.description), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions."""
        logger.exception(f"Excepción no manejada: {error}")
        return jsonify(error="Ocurrió un error inesperado."), 500
