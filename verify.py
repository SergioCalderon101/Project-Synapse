#!/usr/bin/env python
"""
Script de verificación para Synapse AI
Verifica que todas las dependencias estén instaladas y configuradas correctamente.
"""

import sys
from pathlib import Path

def check_python_version():
    """Verificar versión de Python."""
    print("🔍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ es requerido")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Verificar dependencias instaladas."""
    print("\n🔍 Verificando dependencias...")
    
    required = {
        'flask': 'Flask',
        'pydantic': 'Pydantic',
        'pydantic_settings': 'Pydantic Settings',
        'openai': 'OpenAI',
        'flask_cors': 'Flask-CORS',
        'flask_limiter': 'Flask-Limiter',
        'flask_talisman': 'Flask-Talisman',
        'dotenv': 'python-dotenv',
        'filelock': 'filelock'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - NO INSTALADO")
            missing.append(name)
    
    return len(missing) == 0, missing

def check_env_file():
    """Verificar archivo .env."""
    print("\n🔍 Verificando configuración...")
    
    env_file = Path(__file__).parent / '.env'
    env_example = Path(__file__).parent / '.env.example'
    
    if not env_file.exists():
        print(f"⚠️  Archivo .env no encontrado")
        if env_example.exists():
            print(f"💡 Copia .env.example a .env y configura tu API key")
        return False
    
    print(f"✅ Archivo .env encontrado")
    
    # Verificar API key
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'OPENAI_APIKEY=sk-' in content or 'OPENAI_APIKEY="sk-' in content:
            print(f"✅ API key configurada")
            return True
        elif 'OPENAI_APIKEY=' in content:
            print(f"⚠️  API key no configurada en .env")
            print(f"   Edita .env y agrega: OPENAI_APIKEY=sk-tu-api-key")
            return False
    
    return True

def check_project_structure():
    """Verificar estructura del proyecto."""
    print("\n🔍 Verificando estructura del proyecto...")
    
    base_dir = Path(__file__).parent / 'src'
    required_dirs = [
        'core',
        'models',
        'schemas',
        'repositories',
        'services',
        'api',
        'static',
        'templates'
    ]
    
    required_files = [
        'app_new.py',
        'run.py',
        'core/config.py',
        'core/dependencies.py'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - NO ENCONTRADO")
            all_ok = False
    
    for file_name in required_files:
        file_path = base_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name} - NO ENCONTRADO")
            all_ok = False
    
    return all_ok

def main():
    """Función principal."""
    print("="*70)
    print("  SYNAPSE AI - VERIFICACIÓN DE SISTEMA")
    print("="*70)
    
    checks = {
        'Python': check_python_version(),
        'Dependencias': check_dependencies()[0],
        'Configuración': check_env_file(),
        'Estructura': check_project_structure()
    }
    
    print("\n" + "="*70)
    print("  RESUMEN")
    print("="*70)
    
    all_passed = True
    for check_name, passed in checks.items():
        status = "✅ CORRECTO" if passed else "❌ REQUIERE ATENCIÓN"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 ¡Todo está listo!")
        print("Para iniciar la aplicación ejecuta:")
        print("   cd src")
        print("   python run.py")
    else:
        print("\n⚠️  Algunos checks fallaron. Revisa los mensajes arriba.")
        
        # Mostrar dependencias faltantes
        _, missing = check_dependencies()
        if missing:
            print("\nPara instalar dependencias faltantes:")
            print("   pip install -r src/requirements.txt")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
