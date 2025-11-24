# Synapse AI 🚀

> Aplicación de chat web inteligente con modelos de OpenAI, arquitectura limpia y validación con Pydantic.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.9.2-purple.svg)](https://docs.pydantic.dev/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](STATUS.md)

---

## ✨ Características

- 🤖 **Integración con OpenAI** - GPT-3.5, GPT-4, GPT-4o, GPT-4o-mini
- 💬 **Chat Interactivo** - UI moderna con Markdown y syntax highlighting
- 📚 **Gestión de Historial** - Múltiples conversaciones persistentes
- 🏷️ **Títulos Automáticos** - Generación inteligente con IA
- 🔒 **Seguridad** - Rate limiting, CORS, headers de seguridad
- ✅ **Validación** - Pydantic para validación de datos robusta
- 🏗️ **Clean Architecture** - Código modular y mantenible

---

## 📁 Estructura del Proyecto

```
chat_app/
├── 📂 backend/                  # Backend (Python/Flask)
│   ├── 🚀 run.py               # Script de inicio
│   ├── 🎯 app.py               # Factory de aplicación Flask
│   ├── 📋 requirements.txt     # Dependencias Python
│   ├── 🔧 start.bat            # Script inicio Windows
│   ├── 🔧 start.sh             # Script inicio Linux/Mac
│   │
│   ├── api/                    # Capa de presentación (API)
│   │   ├── routes/             # Endpoints REST
│   │   │   ├── chat.py         # CRUD de chats
│   │   │   ├── history.py      # Historial
│   │   │   └── health.py       # Health checks
│   │   └── middleware/
│   │       └── error_handlers.py
│   │
│   ├── core/                   # Configuración y núcleo
│   │   ├── config.py           # Settings con Pydantic
│   │   ├── dependencies.py     # Inyección de dependencias
│   │   └── logging.py          # Sistema de logging
│   │
│   ├── models/                 # Modelos de dominio (Pydantic)
│   │   ├── chat.py             # Chat, ChatMetadata
│   │   └── message.py          # Message
│   │
│   ├── schemas/                # Schemas de request/response
│   │   └── chat.py             # DTOs para API
│   │
│   ├── repositories/           # Capa de persistencia
│   │   ├── chat_repository.py  # Gestión de chats
│   │   ├── metadata_repository.py
│   │   └── file_manager.py     # Operaciones de archivos
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── chat_service.py     # Servicio de chat
│   │   └── openai_service.py   # Integración OpenAI
│   │
│   ├── utils/                  # Utilidades
│   │   └── validators.py       # Validadores
│   │
│   └── data/                   # Datos persistentes
│       ├── chats/              # Conversaciones JSON
│       └── logs/               # Logs de aplicación
│
├── 📂 frontend/                 # Frontend (HTML/CSS/JS)
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Estilos
│   │   ├── js/
│   │   │   └── app.js          # Lógica cliente
│   │   └── favicon.svg
│   └── templates/
│       └── index.html          # UI principal
│
├── 📂 config/                   # Configuración
│   ├── .env                    # Variables de entorno
│   └── .env.example            # Template de configuración
│
├── 📄 README.md                 # Este archivo
├── 📄 STATUS.md                 # Estado del proyecto
├── 📄 QUICKSTART.md             # Guía de inicio rápido
├── 📄 IMPLEMENTATION.md         # Detalles de implementación
└── 📄 DEPLOYMENT.md             # Guía de despliegue
```

---

## 🚀 Inicio Rápido

### 1️⃣ Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/SergioCalderon101/Project-Synapse.git
cd chat_app

# Copiar template de configuración
cp config/.env.example config/.env

# Editar config/.env y agregar tu API key de OpenAI
# OPENAI_APIKEY=sk-tu-api-key-aqui
```

### 2️⃣ Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias

```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Iniciar Aplicación

```bash
cd backend
python run.py
```

🌐 **Acceder a:** http://127.0.0.1:5000

---

## 🛠️ Tecnologías

### Backend
- **Python 3.11+** - Lenguaje principal
- **Flask 3.0.3** - Framework web
- **Pydantic 2.9.2** - Validación de datos
- **pydantic-settings** - Gestión de configuración
- **OpenAI API** - Modelos de IA
- **python-dotenv** - Variables de entorno

### Frontend
- **HTML5 / CSS3** - Estructura y estilos
- **JavaScript ES6+** - Lógica cliente
- **Marked.js** - Renderizado Markdown
- **Highlight.js** - Syntax highlighting

### Seguridad y Calidad
- **Flask-CORS** - Control de orígenes
- **Flask-Limiter** - Rate limiting
- **Flask-Talisman** - Security headers
- **filelock** - Concurrencia segura

---

## 📡 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Frontend (UI) |
| `POST` | `/api/v1/chat` | Crear nuevo chat |
| `GET` | `/api/v1/chat/<id>` | Cargar chat |
| `POST` | `/api/v1/chat/<id>` | Enviar mensaje |
| `DELETE` | `/api/v1/chat/<id>` | Eliminar chat |
| `GET` | `/api/v1/history` | Obtener historial |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/ping` | Ping test |

---

## ⚙️ Configuración (.env)

```env
# OpenAI Configuration
OPENAI_APIKEY=sk-xxx                    # ← REQUERIDO
OPENAI_CHAT_MODEL=gpt-3.5-turbo
OPENAI_TITLE_MODEL=gpt-3.5-turbo

# Flask Configuration
FLASK_DEBUG=True                         # False en producción
PORT=5000
HOST=0.0.0.0

# CORS Configuration
CORS_ORIGINS=*                           # Dominios específicos en producción

# Logging Configuration
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
```

---

## 🔐 Seguridad

**Características implementadas:**
- ✅ Sin credenciales hardcodeadas
- ✅ Variables de entorno para configuración sensible
- ✅ Rate limiting (200 req/día, 50 req/hora, 30 msg/min)
- ✅ Validación de input con Pydantic (1-4000 caracteres)
- ✅ Headers de seguridad HTTP (CSP, HSTS, etc.)
- ✅ CORS configurable
- ✅ File locking para concurrencia
- ✅ `.gitignore` apropiado

**⚠️ Importante:** Antes de desplegar a producción, revisa [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🧪 Testing

```bash
# Health check
curl http://127.0.0.1:5000/api/v1/health

# Response: {"status": "healthy", "service": "Synapse AI"}

# Ping
curl http://127.0.0.1:5000/api/v1/ping

# Response: {"message": "pong"}
```

---

## 📖 Documentación

- 📄 [**STATUS.md**](STATUS.md) - Estado actual del proyecto (Leer primero)
- 🚀 [**QUICKSTART.md**](QUICKSTART.md) - Guía de inicio rápido
- 🏗️ [**IMPLEMENTATION.md**](IMPLEMENTATION.md) - Detalles de implementación
- 🚢 [**DEPLOYMENT.md**](DEPLOYMENT.md) - Guía de despliegue a producción
- 🔧 [**.env.example**](.env.example) - Template de configuración

---

## 🏗️ Arquitectura

### Patrón de Capas

```
┌─────────────────────────────────────┐
│         PRESENTATION LAYER          │
│   (API Routes + Frontend)           │
│   - chat.py, history.py, health.py │
│   - script.js (Frontend)            │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         BUSINESS LOGIC LAYER        │
│   (Services)                        │
│   - ChatService                     │
│   - OpenAIService                   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         DATA ACCESS LAYER           │
│   (Repositories)                    │
│   - ChatRepository                  │
│   - MetadataRepository              │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         DOMAIN LAYER                │
│   (Models + Schemas)                │
│   - Chat, Message, ChatMetadata     │
│   - Pydantic Validation             │
└─────────────────────────────────────┘
```

---

## 💡 Características Destacadas

### Validación con Pydantic

```python
class SendMessageRequest(BaseModel):
    mensaje: str = Field(..., description="User message")
    modelo: Optional[str] = Field(None, description="Model to use")
    
    @field_validator("mensaje")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1:
            raise ValueError("Mensaje vacío.")
        if len(v) > 4000:
            raise ValueError("Mensaje demasiado largo.")
        return v
```

### Inyección de Dependencias

```python
def create_app() -> Flask:
    # Initialize repositories
    chat_repo = ChatRepository()
    metadata_repo = MetadataRepository()
    
    # Initialize services
    openai_service = OpenAIService(openai_client)
    chat_service = ChatService(chat_repo, metadata_repo, openai_service)
    
    # Initialize routes with dependencies
    init_chat_routes(chat_service)
```

### Configuración con Pydantic Settings

```python
class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_APIKEY")
    port: int = Field(5000, alias="PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 👨‍💻 Autor

**Sergio Calderón**
- GitHub: [@SergioCalderon101](https://github.com/SergioCalderon101)
- Repositorio: [Project-Synapse](https://github.com/SergioCalderon101/Project-Synapse)

---

## 🙏 Agradecimientos

- [OpenAI](https://openai.com/) - API de modelos de lenguaje
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Pydantic](https://docs.pydantic.dev/) - Validación de datos
- Comunidad open source por las librerías utilizadas

---

