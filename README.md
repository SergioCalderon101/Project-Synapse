# 🤖 Synapse AI - Chat Web Inteligente

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Descripción

Aplicación web de chat conversacional que integra modelos de IA de OpenAI (GPT-3.5, GPT-4, GPT-4o) mediante una interfaz. Permite crear múltiples conversaciones, cambiar entre modelos, y mantiene historial persistente con generación automática de títulos.

**Características principales:**
- Chat en tiempo real con modelos GPT
- Historial de conversaciones 
- Selección de modelos GPT
- Títulos automáticos generados por IA
- Gestión de contexto (últimos 12 mensajes)
- **Renderizado Markdown** con syntax highlighting
- **Modales profesionales** para confirmaciones
- **Indicadores de progreso** y typing indicators
- **Notificaciones toast** para feedback en tiempo real

## 📁 Estructura del Proyecto

```
chat_app/
├── Project/                  # Carpeta principal
│   ├── app.py               # Backend Flask (600 líneas)
│   ├── requirements.txt     # Dependencias
│   ├── .env                 # Variables de entorno
│   ├── static/              # Frontend
│   │   ├── script.js       # Lógica JS
│   │   └── style.css       # Estilos
│   └── templates/
│       └── index.html       # Interfaz
├── chats/                   # Almacenamiento JSON
│   ├── chats_metadata.json # Índice de chats
│   └── {uuid}.json         # Conversaciones
└── logs/
    └── app.log             # Logs (rotativo, 10MB)
```

##  Tecnologías y Métodos

### **Stack Tecnológico**
- **Backend:** Python, Flask 3.0
- **Frontend:** JavaScript (Vanilla), HTML5, CSS3
- **IA:** OpenAI API (GPT-3.5/4/4o)
- **Renderizado:** Marked.js (Markdown), Highlight.js (Syntax highlighting)
- **Almacenamiento:** JSON (file-based)
- **Dependencias:** flask-cors, python-dotenv, filelock

### **Arquitectura**
- **Patrón:** Cliente-Servidor (3 capas)
- **API:** RESTful (6 endpoints)
- **Diseño:** MVC simplificado
- **Persistencia:** File-based storage

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- API Key de OpenAI ([obtener aquí](https://platform.openai.com/api-keys))
- Git (opcional)

### Pasos de Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/SergioCalderon101/Project-Synapse.git
cd Project-Synapse

# 2. Crear entorno virtual
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# 3. Instalar dependencias
cd Project
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu OPENAI_APIKEY

# 5. Ejecutar servidor
python app.py
```

**Acceder a la aplicación:** [http://localhost:5000](http://localhost:5000)

## 🔧 Variables de Entorno

| Variable | Descripción | Valor por Defecto | Requerido |
|----------|-------------|-------------------|-----------|
| `OPENAI_APIKEY` | API Key de OpenAI | - | ✅ Sí |
| `OPENAI_CHAT_MODEL` | Modelo para conversaciones | `gpt-3.5-turbo` | ❌ No |
| `OPENAI_TITLE_MODEL` | Modelo para títulos | `gpt-3.5-turbo` | ❌ No |
| `FLASK_DEBUG` | Modo debug | `False` | ❌ No |
| `LOG_LEVEL` | Nivel de logs | `INFO` | ❌ No |
| `PORT` | Puerto del servidor | `5000` | ❌ No |
| `CORS_ORIGINS` | Orígenes CORS permitidos | `*` | ❌ No |

Ver archivo [`.env.example`](Project/.env.example) para más detalles.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Sergio Calderon**

- GitHub: [@SergioCalderon101](https://github.com/SergioCalderon101)
- Repositorio: [Project-Synapse](https://github.com/SergioCalderon101/Project-Synapse)

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva característica'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚠️ Disclaimer

Este proyecto usa la API de OpenAI. Los costos de uso de la API son responsabilidad del usuario. Consulta los [precios de OpenAI](https://openai.com/pricing) para más información.
