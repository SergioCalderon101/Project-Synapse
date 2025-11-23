
"""
Script de inicio para Synapse AI

Este script inicia el servidor de desarrollo de Flask.
Para producción, usar un servidor WSGI como Gunicorn o uWSGI.
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Agregar directorio src al path
    src_dir = Path(__file__).parent
    sys.path.insert(0, str(src_dir))
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Importar app
    from app_new import app, settings
    
    print("\n" + "="*70)
    print("  🚀 Iniciando Synapse AI (Versión Refactorizada)")
    print("="*70)
    
    # Verificar API key
    if not settings.openai_api_key:
        print("\n⚠️  ADVERTENCIA: OPENAI_APIKEY no configurada")
        print("   Edita el archivo .env y agrega tu API key de OpenAI\n")
    
    print(f"📍 Servidor: http://{settings.host}:{settings.port}")
    print(f"🔧 Debug: {settings.flask_debug}")
    print(f"📝 Log Level: {settings.log_level}")
    print("="*70 + "\n")
    
    # Ejecutar servidor
    try:
        app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.flask_debug,
            threaded=True,
            use_reloader=settings.flask_debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")
        sys.exit(1)
