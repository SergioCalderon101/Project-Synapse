"""Health check routes blueprint."""
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__, url_prefix='/api/v1')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        "status": "healthy",
        "service": "Synapse AI"
    }), 200


@health_bp.route('/ping', methods=['GET'])
def ping():
    """Ping endpoint.
    
    Returns:
        200: Pong
    """
    return jsonify({"message": "pong"}), 200
