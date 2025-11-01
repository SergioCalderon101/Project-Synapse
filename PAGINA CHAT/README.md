# Synapse AI - Chat Web con Generación de PDF

Este proyecto es una aplicación web de chat basada en Flask que utiliza modelos de OpenAI para responder preguntas y puede generar respuestas en PDF bajo demanda. Incluye una interfaz moderna, historial de chats y selección de modelo AI.

## Estructura de Carpetas

```
PAGINA CHAT/
│   app.py                # Lógica principal del backend Flask
│   requirements.txt      # Dependencias del proyecto
│   .env                  # Variables de entorno (API keys, etc.)
│
├── static/               # Archivos estáticos (JS, CSS, PDFs generados)
│   ├── script.js         # Lógica frontend (JS)
│   ├── style.css         # Estilos de la interfaz
│   └── respuesta_*.pdf   # PDFs generados por el sistema
│
├── templates/            # Plantillas HTML para Flask
│   ├── index.html        # Interfaz principal del chat
│   └── respuesta_pdf.html# Plantilla para generación de PDFs
│
├── pdfs/                 # PDFs subidos o de ejemplo (no se modifican)
│   └── *.pdf
```

## ¿Cómo funciona?
- El usuario interactúa con el chat en la web.
- El backend responde usando OpenAI (GPT-3.5, GPT-4, etc.).
- Si el usuario solicita un PDF, la respuesta se genera y descarga como PDF.
- El historial de chats y títulos se guarda automáticamente.

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
- weasyprint
- python-dotenv
- filelock

## Notas
- Los archivos en `pdfs/` son ejemplos o subidos, no se modifican.
- Los PDFs generados por el sistema se guardan en `static/`.
- El archivo `tempCodeRunnerFile.py` ha sido eliminado por no ser necesario.

---

¡Listo para usar y modificar según tus necesidades!
