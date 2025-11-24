"""Flask application factory and initialization."""
from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

from core.config import settings
from core.logging import setup_logging, get_logger
from core.dependencies import dependencies
from repositories.chat_repository import ChatRepository
from repositories.metadata_repository import MetadataRepository
from services.chat_service import ChatService
from services.openai_service import OpenAIService
from api.routes.chat import chat_bp, init_chat_routes
from api.routes.history import history_bp, init_history_routes
from api.routes.health import health_bp
from api.middleware.error_handlers import register_error_handlers

logger = get_logger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application.
    
    Returns:
        Configured Flask application
    """
    app = Flask(
        __name__,
        template_folder=str(settings.templates_folder),
        static_folder=str(settings.static_folder)
    )
    
    setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file,
        app_logger=app.logger
    )
    
    cors_origins = settings.cors_origins_list
    CORS(app, origins=cors_origins, supports_credentials=True)
    logger.info(f"CORS configurado con orígenes: {cors_origins}")
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[
            f"{settings.rate_limit_per_day} per day",
            f"{settings.rate_limit_per_hour} per hour"
        ],
        storage_uri="memory://"
    )
    
    @limiter.limit(f"{settings.rate_limit_chat_per_minute} per minute")
    def rate_limited_chat():
        pass
    
    logger.info("Rate limiting configurado")
    
    if not settings.flask_debug:
        Talisman(
            app,
            content_security_policy={
                'default-src': "'self'",
                'script-src': [
                    "'self'",
                    "'unsafe-inline'",
                    'https://cdn.jsdelivr.net',
                    'https://unpkg.com'
                ],
                'style-src': [
                    "'self'",
                    "'unsafe-inline'",
                    'https://fonts.googleapis.com',
                    'https://unpkg.com',
                    'https://cdn.jsdelivr.net'
                ],
                'font-src': [
                    "'self'",
                    'https://fonts.gstatic.com',
                    'https://unpkg.com'
                ]
            },
            force_https=False
        )
        logger.info("Talisman (security headers) configurado")
    
    openai_client = dependencies.openai_client
    if not openai_client:
        logger.warning("OpenAI client no inicializado. Funcionalidad AI limitada.")
    
    chat_repo = ChatRepository()
    metadata_repo = MetadataRepository()
    
    openai_service = OpenAIService(openai_client)
    chat_service = ChatService(chat_repo, metadata_repo, openai_service)
    
    init_chat_routes(chat_service)
    init_history_routes(chat_service)
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(health_bp)
    
    logger.info("Blueprints registrados")
    
    register_error_handlers(app)
    
    @app.route('/')
    def home():
        """Serve main HTML interface."""
        try:
            return render_template('index.html')
        except Exception as e:
            app.logger.exception(f"Error renderizando index.html: {e}")
            return "Error UI.", 500
    
    return app


def print_startup_banner() -> None:
    """Print startup banner with server information."""
    print("\n" + "="*60)
    print(" Synapse AI Server")
    print("="*60)
    print(f" Modo Debug: {settings.flask_debug}")
    print(f" Log Level: {settings.log_level}")
    print(f" CORS: {settings.cors_origins}")
    print(f" Puerto: {settings.port}")
    print(f" URL: http://127.0.0.1:{settings.port}")
    print(f" API: http://127.0.0.1:{settings.port}/api/v1")
    print("="*60 + "\n")
