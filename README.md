# 🤖 Synapse AI - Chat Web Inteligente

## 📝 Descripción

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

## 🛠️ Tecnologías y Métodos

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

### **Metodologías**
- **Concurrencia:** FileLock (thread-safe)
- **Logging:** RotatingFileHandler (5 backups)
- **Seguridad:** Variables de entorno, validación de entrada
- **Context Management:** Ventana deslizante (12 mensajes)
- **Error Handling:** Try-except completo en todas las rutas

## 🚀 Instalación Rápida

```bash
# 1. Clonar repositorio
git clone https://github.com/SergioCalderon101/Project-Synapse.git
cd chat_app/Project

# 2. Crear entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
echo OPENAI_APIKEY=sk-tu-clave-aqui > .env

# 5. Ejecutar
python app.py
```

Acceder en: [http://localhost:5000](http://localhost:5000)

---

**Autor:** Sergio Calderon  
**GitHub:** [@SergioCalderon101](https://github.com/SergioCalderon101)  
**Repositorio:** [Prject-Synapse](https://github.com/SergioCalderon101/Project-Synapse)
