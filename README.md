# 🤖 Synapse AI - Chat Web Inteligente

Aplicación web de chat moderna y profesional basada en Flask que utiliza modelos de OpenAI (GPT-3.5, GPT-4, GPT-4o) para proporcionar respuestas inteligentes y contextuales. Incluye interfaz intuitiva, historial persistente de conversaciones, generación automática de títulos y selección dinámica de modelos.

## 📁 Estructura del Proyecto

```
chat_app/
│
├── PAGINA CHAT/
│   ├── app.py                    # Backend Flask principal
│   ├── requirements.txt          # Dependencias Python
│   ├── .env                      # Variables de entorno (API keys)
│   │
│   ├── static/                   # Archivos estáticos
│   │   ├── script.js            # Lógica frontend
│   │   └── style.css            # Estilos CSS
│   │
│   └── templates/                # Plantillas HTML
│       └── index.html           # Interfaz principal
│
├── chats/                        # Sistema de almacenamiento
│   ├── chats_metadata.json      # Índice de todos los chats
│   └── {uuid}.json              # Archivos de conversaciones
│
└── logs/                         # Sistema de logging
    └── app.log                  # Logs de la aplicación
```

## ✨ Características Principales

### 🎯 **Funcionalidades del Chat**
- **Múltiples Modelos AI**: Soporte para GPT-3.5 Turbo, GPT-4, GPT-4o y GPT-4o Mini
- **Historial Persistente**: Todas las conversaciones se guardan automáticamente
- **Títulos Automáticos**: La IA genera títulos descriptivos después de 5+ mensajes
- **Gestión de Contexto**: Mantiene los últimos 12 mensajes para optimizar respuestas
- **Interfaz Responsiva**: Diseño moderno adaptable a cualquier dispositivo

### 🔧 **Características Técnicas**
- **Backend Robusto**: Flask con manejo de errores completo
- **Concurrencia Segura**: FileLock para operaciones thread-safe
- **Logging Avanzado**: Sistema de logs rotativo con múltiples niveles
- **CORS Configurable**: Soporte para múltiples orígenes
- **API RESTful**: Endpoints bien estructurados y documentados

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- Cuenta de OpenAI con API Key
- pip (gestor de paquetes Python)

### Instalación Paso a Paso

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/SergioCalderon101/chatbot.git
   cd chat_app/PAGINA\ CHAT
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crea un archivo `.env` en la carpeta `PAGINA CHAT`:
   ```env
   OPENAI_APIKEY=sk-tu-clave-aqui
   OPENAI_CHAT_MODEL=gpt-3.5-turbo
   OPENAI_TITLE_MODEL=gpt-3.5-turbo
   LOG_LEVEL=INFO
   FLASK_DEBUG=True
   CORS_ORIGINS=*
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Acceder a la interfaz**
   
   Abre tu navegador en: [http://localhost:5000](http://localhost:5000)

## 📦 Dependencias

```txt
Flask>=3.0.0
flask-cors>=4.0.0
openai>=1.0.0
python-dotenv>=1.0.0
filelock>=3.13.0
```

## 🔌 API Endpoints

### **Chat Management**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Interfaz principal del chat |
| `POST` | `/new_chat` | Crear nuevo chat |
| `GET` | `/history` | Obtener historial de chats |
| `GET` | `/chat/<chat_id>` | Cargar chat específico |
| `POST` | `/chat/<chat_id>` | Enviar mensaje al chat |
| `DELETE` | `/chat/<chat_id>` | Eliminar chat |

### **Ejemplo de Uso**

**Crear nuevo chat:**
```bash
curl -X POST http://localhost:5000/new_chat
```

**Enviar mensaje:**
```bash
curl -X POST http://localhost:5000/chat/{chat_id} \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola, ¿cómo estás?", "modelo": "gpt-4"}'
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `OPENAI_APIKEY` | Tu API Key de OpenAI | *(requerido)* |
| `OPENAI_CHAT_MODEL` | Modelo para chat | `gpt-3.5-turbo` |
| `OPENAI_TITLE_MODEL` | Modelo para títulos | `gpt-3.5-turbo` |
| `LOG_LEVEL` | Nivel de logging | `INFO` |
| `FLASK_DEBUG` | Modo debug Flask | `True` |
| `CORS_ORIGINS` | Orígenes CORS permitidos | `*` |

### Modelos Soportados
- `gpt-3.5-turbo` - Rápido y económico
- `gpt-4` - Mayor capacidad de razonamiento
- `gpt-4o` - Optimizado y eficiente
- `gpt-4o-mini` - Versión ligera de GPT-4o

### Configuración de Límites
```python
MAX_TITLE_LENGTH = 40           # Longitud máxima del título
MAX_CONTEXT_LENGTH = 12         # Mensajes en contexto
TITLE_GENERATION_MIN_MESSAGES = 5  # Mensajes mínimos para generar título
```

## 📝 Sistema de Logging

Los logs se guardan en `logs/app.log` con rotación automática:
- **Tamaño máximo**: 10MB por archivo
- **Archivos de backup**: 5
- **Niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🛡️ Seguridad

- ✅ Validación de entrada en todos los endpoints
- ✅ Manejo seguro de archivos con FileLock
- ✅ Variables de entorno para datos sensibles
- ✅ Logging de todas las operaciones críticas
- ✅ Manejo robusto de errores y excepciones

## 🎨 Interfaz de Usuario

- **Diseño Moderno**: Interfaz limpia y profesional
- **Selector de Modelo**: Cambia entre modelos AI fácilmente
- **Historial Lateral**: Acceso rápido a conversaciones previas
- **Markdown Support**: Renderizado de respuestas con formato
- **Responsive**: Funciona en móviles, tablets y escritorio

## 🔧 Solución de Problemas

### Error: "OPENAI_APIKEY no configurada"
- Verifica que el archivo `.env` existe
- Asegúrate de que la variable `OPENAI_APIKEY` esté definida
- Reinicia la aplicación después de crear el `.env`

### Error: "Unable to import 'flask'"
```bash
pip install -r requirements.txt
```

### El chat no guarda el historial
- Verifica permisos de escritura en la carpeta `chats/`
- Revisa los logs en `logs/app.log` para más detalles

## 📊 Estructura de Datos

### Formato de Chat (`{uuid}.json`)
```json
[
  {
    "role": "system",
    "content": "Eres Synapse AI..."
  },
  {
    "role": "user",
    "content": "Hola"
  },
  {
    "role": "assistant",
    "content": "¡Hola! ¿En qué puedo ayudarte?"
  }
]
```

### Formato de Metadata (`chats_metadata.json`)
```json
{
  "chat-uuid": {
    "id": "chat-uuid",
    "title": "Título generado",
    "created_at": "2025-11-12T10:30:00.000Z",
    "last_updated": "2025-11-12T10:45:00.000Z"
  }
}
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 👤 Autor

**Sergio Calderon**
- GitHub: [@SergioCalderon101](https://github.com/SergioCalderon101)
- Repositorio: [chatbot](https://github.com/SergioCalderon101/chatbot)

## 🙏 Agradecimientos

- OpenAI por proporcionar las APIs de modelos GPT
- Flask por el framework web
- La comunidad de código abierto

---

**⭐ Si te gusta este proyecto, considera darle una estrella en GitHub!**
