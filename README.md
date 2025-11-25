# Synapse AI

Aplicación de chat web con integración de modelos de OpenAI.

## Características

- Chat interactivo con múltiples modelos de OpenAI
- Gestión de historial de conversaciones
- Generación automática de títulos con IA
- Renderizado de Markdown y syntax highlighting
- Arquitectura limpia con separación de capas
- Validación de datos con Pydantic

## Estructura del Proyecto

```
chat_app/
├── backend/
│   ├── app.py
│   ├── factory.py
│   ├── requirements.txt
│   ├── start.bat
│   ├── start.sh
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   └── error_handlers.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py
│   │       ├── health.py
│   │       └── history.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── logging.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── message.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── chat_repository.py
│   │   ├── file_manager.py
│   │   └── metadata_repository.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── chat.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py
│   │   └── openai_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py
│   └── data/
│       ├── chats/
│       └── logs/
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── components/
│   │       │   ├── LoadingOverlay.js
│   │       │   ├── Modal.js
│   │       │   └── Toast.js
│   │       ├── config/
│   │       │   └── app.config.js
│   │       ├── core/
│   │       │   └── App.js
│   │       ├── features/
│   │       │   ├── chat/
│   │       │   │   ├── ChatController.js
│   │       │   │   └── ChatView.js
│   │       │   ├── history/
│   │       │   │   ├── HistoryController.js
│   │       │   │   └── HistoryView.js
│   │       │   └── settings/
│   │       │       ├── SettingsController.js
│   │       │       └── SettingsView.js
│   │       ├── services/
│   │       │   ├── ChatService.js
│   │       │   ├── HistoryService.js
│   │       │   └── HttpClient.js
│   │       ├── state/
│   │       │   ├── AppState.js
│   │       │   └── Store.js
│   │       └── utils/
│   │           ├── dom.js
│   │           ├── markdown.js
│   │           └── validators.js
│   └── templates/
│       └── index.html
├── config/
│   ├── .env
│   └── .env.example
├── DEPLOYMENT.md
├── FRONTEND_MIGRATION.md
├── IMPLEMENTATION.md
├── QUICKSTART.md
└── README.md
```

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/SergioCalderon101/Project-Synapse.git
cd chat_app

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r backend/requirements.txt

# Configurar variables de entorno
cp config/.env.example config/.env
# Editar config/.env y agregar tu OPENAI_APIKEY
```

## Uso

```bash
cd backend
python run.py
```

Acceder a http://127.0.0.1:5000

## Tecnologías

- **Backend**: Python, Flask, Pydantic, OpenAI API
- **Frontend**: HTML, CSS, JavaScript, Marked.js, Highlight.js
- **Seguridad**: Flask-CORS, Flask-Limiter, Flask-Talisman

## Configuración

Variables principales en `config/.env`:

```env
OPENAI_APIKEY=sk-xxx          # Requerido
OPENAI_CHAT_MODEL=gpt-3.5-turbo
PORT=5000
FLASK_DEBUG=True
```

## API Endpoints

- `POST /api/v1/chat` - Crear nuevo chat
- `GET /api/v1/chat/<id>` - Cargar chat
- `POST /api/v1/chat/<id>` - Enviar mensaje
- `DELETE /api/v1/chat/<id>` - Eliminar chat
- `GET /api/v1/history` - Obtener historial
- `GET /api/v1/health` - Health check

