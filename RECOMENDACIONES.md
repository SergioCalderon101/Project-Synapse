# Recomendaciones de Mejoras - Project Synapse

Este documento contiene recomendaciones específicas para mejorar la seguridad, rendimiento y mantenibilidad del proyecto.

---

## 🔐 Seguridad

### 1. Validación de Input del Usuario

**Prioridad:** ALTA

**Problema Actual:**
El input del usuario solo se valida con `.strip()`, sin límites de longitud ni sanitización adicional.

**Solución Recomendada:**

Agregar a la clase `Config` en `app.py`:
```python
class Config:
    # ... código existente ...
    
    # Validación de input
    MAX_MESSAGE_LENGTH: int = 4000  # Máximo de caracteres por mensaje
    MIN_MESSAGE_LENGTH: int = 1     # Mínimo de caracteres
```

Actualizar la función `process_chat_message` en `app.py`:
```python
@app.route("/chat/<chat_id>", methods=["POST"])
def process_chat_message(chat_id: str) -> Tuple[Any, int]:
    # ... código existente hasta la validación ...
    
    try:
        user_input = data["mensaje"].strip()
    except (KeyError, AttributeError, TypeError) as e:
        app.logger.warning(f"Campo 'mensaje' inválido (chat: {chat_id}): {e}")
        return jsonify({"error": "Campo 'mensaje' inválido."}), 400
    
    # NUEVA VALIDACIÓN
    if len(user_input) < config.MIN_MESSAGE_LENGTH:
        app.logger.warning(f"Mensaje vacío (chat: {chat_id})")
        return jsonify({"error": "Mensaje vacío."}), 400
    
    if len(user_input) > config.MAX_MESSAGE_LENGTH:
        app.logger.warning(f"Mensaje demasiado largo (chat: {chat_id}): {len(user_input)} chars")
        return jsonify({
            "error": f"Mensaje demasiado largo. Máximo {config.MAX_MESSAGE_LENGTH} caracteres."
        }), 400
    
    # ... resto del código ...
```

### 2. Rate Limiting

**Prioridad:** ALTA (si se despliega públicamente)

**Problema:**
Sin rate limiting, el servicio es vulnerable a abuso y puede incurrir en costos excesivos de API.

**Solución Recomendada:**

Instalar Flask-Limiter:
```bash
pip install Flask-Limiter
```

Agregar a `requirements.txt`:
```
Flask-Limiter==3.5.0
```

Implementar en `app.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Después de inicializar Flask
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Aplicar límites específicos a endpoints críticos
@app.route("/chat/<chat_id>", methods=["POST"])
@limiter.limit("30 per minute")  # Máximo 30 mensajes por minuto
def process_chat_message(chat_id: str) -> Tuple[Any, int]:
    # ... código existente ...
```

### 3. Configuración CORS para Producción

**Prioridad:** MEDIA

**Problema:**
El valor por defecto `CORS_ORIGINS=*` permite acceso desde cualquier origen.

**Solución Recomendada:**

Actualizar `.env.example` con advertencias más claras:
```bash
# -----------------------------------------------------------------------------
# CORS - Configuración de seguridad (IMPORTANTE)
# -----------------------------------------------------------------------------
# ⚠️ ADVERTENCIA DE SEGURIDAD:
# - En DESARROLLO: Puedes usar * para permitir todos los orígenes
# - En PRODUCCIÓN: DEBES especificar dominios exactos
# 
# Ejemplos seguros para producción:
# CORS_ORIGINS=https://tu-dominio.com
# CORS_ORIGINS=https://app.ejemplo.com,https://www.ejemplo.com
#
# ⛔ NO usar * en producción - esto permite ataques CSRF
CORS_ORIGINS=*
```

Crear archivo `PRODUCTION.md`:
```markdown
# Checklist de Configuración para Producción

## Variables de Entorno Críticas

### CORS_ORIGINS
❌ MAL: `CORS_ORIGINS=*`  
✅ BIEN: `CORS_ORIGINS=https://tu-dominio.com`

### FLASK_DEBUG
❌ MAL: `FLASK_DEBUG=True`  
✅ BIEN: `FLASK_DEBUG=False`

### LOG_LEVEL
❌ MAL: `LOG_LEVEL=DEBUG`  
✅ BIEN: `LOG_LEVEL=WARNING` o `LOG_LEVEL=ERROR`

## Checklist de Seguridad

- [ ] CORS_ORIGINS configurado con dominios específicos
- [ ] FLASK_DEBUG=False
- [ ] LOG_LEVEL=WARNING o superior
- [ ] Rate limiting activado
- [ ] HTTPS configurado
- [ ] API keys rotadas desde desarrollo
- [ ] Backups configurados para /chats
- [ ] Monitoreo de errores activo
```

### 4. Headers de Seguridad HTTP

**Prioridad:** MEDIA

**Solución Recomendada:**

Instalar Flask-Talisman:
```bash
pip install flask-talisman
```

Implementar en `app.py`:
```python
from flask_talisman import Talisman

# Después de inicializar Flask
if not config.FLASK_DEBUG:
    Talisman(app, 
        content_security_policy={
            'default-src': "'self'",
            'script-src': [
                "'self'",
                'https://cdn.jsdelivr.net',
                'https://unpkg.com'
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Necesario para algunos estilos inline
                'https://fonts.googleapis.com',
                'https://unpkg.com',
                'https://cdn.jsdelivr.net'
            ],
            'font-src': [
                "'self'",
                'https://fonts.gstatic.com'
            ]
        },
        force_https=True
    )
```

---

## 🧪 Testing

### 5. Tests Unitarios

**Prioridad:** MEDIA

**Solución Recomendada:**

Crear estructura de tests:
```
Project/
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_file_manager.py
│   ├── test_chat_manager.py
│   ├── test_api_endpoints.py
│   └── conftest.py
```

Agregar dependencias de testing a `requirements.txt`:
```
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
```

Ejemplo de test básico (`tests/test_config.py`):
```python
import pytest
from app import Config

def test_config_defaults():
    """Test que los valores por defecto están configurados."""
    assert Config.MAX_TITLE_LENGTH == 40
    assert Config.MAX_CONTEXT_LENGTH == 12
    assert Config.OPENAI_CHAT_MODEL == "gpt-3.5-turbo"

def test_validate_model():
    """Test validación de modelos."""
    assert Config.validate_model("gpt-4") == "gpt-4"
    assert Config.validate_model("invalid-model") == Config.OPENAI_CHAT_MODEL
```

Ejemplo de test de endpoint (`tests/test_api_endpoints.py`):
```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    """Test que la página principal carga."""
    response = client.get('/')
    assert response.status_code == 200

def test_new_chat_endpoint(client):
    """Test creación de nuevo chat."""
    response = client.post('/new_chat')
    assert response.status_code == 201
    data = response.get_json()
    assert 'chat_id' in data
    assert 'messages' in data

def test_message_too_long(client):
    """Test que mensajes muy largos son rechazados."""
    # Primero crear un chat
    response = client.post('/new_chat')
    chat_id = response.get_json()['chat_id']
    
    # Intentar enviar mensaje muy largo
    long_message = "a" * 5000
    response = client.post(
        f'/chat/{chat_id}',
        json={'mensaje': long_message}
    )
    assert response.status_code == 400
```

---

## 📚 Documentación

### 6. Documentación de API

**Prioridad:** BAJA

**Solución Recomendada:**

Opción 1 - Swagger/OpenAPI (recomendado):
```bash
pip install flask-swagger-ui
```

Opción 2 - Documentación manual mejorada en `README.md`:
```markdown
## API Endpoints

### POST /new_chat
Crea un nuevo chat.

**Response:**
```json
{
  "chat_id": "uuid",
  "messages": [...],
  "title": "Nuevo Chat"
}
```

### GET /history
Obtiene el historial de chats.

**Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "title": "Título del chat",
      "created_at": "ISO-8601",
      "last_updated": "ISO-8601"
    }
  ]
}
```

### GET /chat/<chat_id>
Carga un chat específico.

**Parameters:**
- `chat_id` (string): UUID del chat

**Response:**
```json
{
  "chat_id": "uuid",
  "messages": [...],
  "title": "Título"
}
```

### POST /chat/<chat_id>
Envía un mensaje al chat.

**Parameters:**
- `chat_id` (string): UUID del chat

**Body:**
```json
{
  "mensaje": "texto del mensaje",
  "modelo": "gpt-3.5-turbo" // opcional
}
```

**Response:**
```json
{
  "respuesta": "respuesta del AI",
  "timestamp": "ISO-8601",
  "new_title": "título actualizado" // si aplica
}
```

### DELETE /chat/<chat_id>
Elimina un chat.

**Parameters:**
- `chat_id` (string): UUID del chat

**Response:**
```json
{
  "message": "Chat eliminado."
}
```
```

---

## 🎨 Mejoras de Código

### 7. Variables CSS Reutilizables

**Prioridad:** BAJA

**Solución Recomendada:**

Agregar al inicio de `style.css`:
```css
:root {
    /* Colores principales */
    --color-bg-primary: #111827;
    --color-bg-secondary: #1F2937;
    --color-bg-tertiary: #374151;
    --color-bg-quaternary: #4B5563;
    
    --color-text-primary: #F9FAFB;
    --color-text-secondary: #E5E7EB;
    --color-text-tertiary: #D1D5DB;
    --color-text-muted: #9CA3AF;
    
    --color-accent-blue: #60A5FA;
    --color-accent-blue-dark: #2563EB;
    --color-accent-green: #10B981;
    --color-accent-red: #EF4444;
    
    /* Espaciado */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 24px;
    
    /* Bordes */
    --border-radius-sm: 6px;
    --border-radius-md: 8px;
    --border-radius-lg: 12px;
    
    /* Transiciones */
    --transition-fast: 0.2s ease;
    --transition-normal: 0.3s ease;
}

/* Luego usar las variables */
.sidebar {
    background-color: var(--color-bg-secondary);
    border-right: 1px solid var(--color-bg-tertiary);
    padding: var(--spacing-lg);
}
```

### 8. Separación de Concerns en JavaScript

**Prioridad:** BAJA

**Solución Recomendada:**

Considerar dividir `script.js` en módulos más pequeños:
```
static/
├── js/
│   ├── config.js       // Configuración y constantes
│   ├── ui.js          // Funciones de UI
│   ├── api.js         // Llamadas a API
│   ├── chat.js        // Lógica de chat
│   ├── history.js     // Gestión de historial
│   └── main.js        // Inicialización
```

---

## 📊 Monitoreo y Observabilidad

### 9. Integración con Sentry

**Prioridad:** BAJA (MEDIA en producción)

**Solución Recomendada:**

```bash
pip install sentry-sdk[flask]
```

Agregar a `app.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Solo en producción
if not config.FLASK_DEBUG and os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
        environment="production"
    )
```

---

## 🚀 Rendimiento

### 10. Caché para Metadata

**Prioridad:** BAJA

**Problema:**
La metadata se lee del archivo en cada request de historial.

**Solución Recomendada:**

Implementar caché simple en memoria:
```python
from functools import lru_cache
from time import time

class MetadataManager:
    def __init__(self):
        self.lock = FileLock(config.METADATA_LOCK_FILE)
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 60  # 60 segundos
    
    def load(self) -> Dict[str, Dict[str, Any]]:
        """Carga metadata con caché simple."""
        current_time = time()
        
        # Usar caché si está fresco
        if self._cache and (current_time - self._cache_time) < self._cache_ttl:
            return self._cache.copy()
        
        # Cargar desde archivo
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
        
        # Actualizar caché
        self._cache = metadata
        self._cache_time = current_time
        
        return metadata.copy()
    
    def save(self, metadata: Dict[str, Dict[str, Any]]) -> None:
        """Guarda metadata e invalida caché."""
        FileManager.ensure_directory_exists(config.CHATS_DIR)
        
        try:
            with self.lock.acquire(timeout=5):
                if FileManager.write_json_file(config.METADATA_FILE, metadata):
                    # Invalidar caché
                    self._cache = None
                    self._cache_time = 0
                    app.logger.debug(
                        f"Metadata guardada en {config.METADATA_FILE} ({len(metadata)} chats)")
        except TimeoutError:
            app.logger.error(f"Timeout esperando lock para guardar {config.METADATA_FILE}.")
        except Exception as e:
            app.logger.exception(f"Error inesperado guardando metadata: {e}")
```

---

## 📝 Implementación Sugerida

### Orden de Implementación:

1. **Semana 1 - Seguridad Crítica:**
   - [ ] Validación de input (#1)
   - [ ] Configuración CORS para producción (#3)
   - [ ] Crear PRODUCTION.md

2. **Semana 2 - Rate Limiting y Monitoreo:**
   - [ ] Implementar rate limiting (#2)
   - [ ] Headers de seguridad (#4)
   - [ ] Integrar Sentry (opcional)

3. **Semana 3 - Testing:**
   - [ ] Setup de pytest
   - [ ] Tests básicos de endpoints
   - [ ] Tests de validación

4. **Semana 4 - Mejoras Menores:**
   - [ ] Documentación de API
   - [ ] Variables CSS
   - [ ] Optimización de caché

---

## 📧 Soporte

Si tienes preguntas sobre estas recomendaciones, consulta:
- `SECURITY_AUDIT.md` para el análisis completo
- Issues en GitHub para discusión
- Documentación oficial de las librerías mencionadas

**Última actualización:** 21 de Noviembre, 2025
