"""Main entry point for Synapse AI application."""
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from factory import create_app, print_startup_banner
from core.config import settings


if __name__ == "__main__":
    # Print startup banner
    print_startup_banner()
    
    # Warn if no API key
    if not settings.openai_api_key:
        print("⚠️  ADVERTENCIA: OPENAI_APIKEY no configurada", file=sys.stderr)
        print("   Edita config/.env y agrega tu API key\n", file=sys.stderr)
    
    # Create and run app
    app = create_app()
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.flask_debug,
        threaded=True,
        use_reloader=settings.flask_debug
    )
