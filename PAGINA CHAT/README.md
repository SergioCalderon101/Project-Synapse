# Synapse AI - Chat Web Inteligente

Este proyecto es una aplicación web de chat basada en Flask que utiliza modelos de OpenAI para responder preguntas de manera inteligente. Incluye una interfaz moderna, historial de chats y selección de modelo AI.

## Estructura de Carpetas

```
PAGINA CHAT/
│   app.py                # Lógica principal del backend Flask
│   requirements.txt      # Dependencias del proyecto
│   .env                  # Variables de entorno (API keys, etc.)
│
├── static/               # Archivos estáticos (JS, CSS)
│   ├── script.js         # Lógica frontend (JS)
│   └── style.css         # Estilos de la interfaz
│
├── templates/            # Plantillas HTML para Flask
│   └── index.html        # Interfaz principal del chat
│
├── chats/                # Historial de conversaciones guardadas
│   ├── chats_metadata.json
│   └── [uuid].json       # Archivos de chat individuales
│
└── logs/                 # Archivos de log de la aplicación
    └── app.log
```

## ¿Cómo funciona?
- El usuario interactúa con el chat en la web.
- El backend responde usando OpenAI (GPT-3.5, GPT-4, GPT-4o, etc.).
- El historial de chats y títulos se guarda automáticamente.
- Interfaz moderna con soporte para múltiples modelos de AI.

## Instalación rápida
1. Clona este repositorio y entra a la carpeta `PAGINA CHAT`.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Crea un archivo `.env` con tu clave de OpenAI:
   ```env
   OPENAI_APIKEY=sk-...
   ```
4. Ejecuta la app:
   ```bash
   python app.py
   ```
5. Abre tu navegador en [http://localhost:5000](http://localhost:5000)

## Dependencias principales
- Flask
- Flask-CORS
- openai
- python-dotenv
- filelock

## Características
- Chat inteligente con múltiples modelos de OpenAI
- Historial persistente de conversaciones
- Interfaz web moderna y responsiva
- Selección dinámica de modelo AI
- Gestión automática de títulos de chat
- Sistema de logs robusto
- Manejo seguro de archivos con FileLock

---

¡Listo para usar y modificar según tus necesidades!
