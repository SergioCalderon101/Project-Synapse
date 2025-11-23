# Synapse AI

Aplicación de chat web que integra modelos de OpenAI con gestión de historial de conversaciones y generación automática de títulos.

## 📁 Estructura

```
Project/
├── app.py              # Backend Flask
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de variables de entorno
├── static/
│   ├── script.js      # Lógica del cliente
│   └── style.css      # Estilos
├── templates/
│   └── index.html     # Interfaz
├── chats/             # Almacenamiento de conversaciones
└── logs/              # Logs de la aplicación
```

## 🛠️ Tecnologías

- **Backend:** Python, Flask, OpenAI API
- **Frontend:** HTML5, CSS3, JavaScript

## ⚙️ Configuración

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp Project/.env.example Project/.env
   ```

2. Edita `.env` y configura tu API key de OpenAI:
   ```bash
   OPENAI_APIKEY=tu-api-key-aqui
   ```

3. Instala las dependencias:
   ```bash
   pip install -r Project/requirements.txt
   ```

4. Ejecuta la aplicación:
   ```bash
   python Project/app.py
   ```

## 🔐 Seguridad

**Características implementadas:**
- ✅ Sin credenciales hardcodeadas
- ✅ Variables de entorno para configuración sensible
- ✅ Rate limiting (200 req/día, 50 req/hora, 30 msg/min)
- ✅ Validación de input (1-4000 caracteres)
- ✅ Headers de seguridad HTTP (CSP, HSTS, etc.)
- ✅ `.gitignore` apropiado

**⚠️ Importante:** Antes de desplegar a producción, revisa [DEPLOYMENT.md](DEPLOYMENT.md) para configuración segura y checklist completo.
