# Synapse AI

Aplicación de chat web que integra modelos de OpenAI con gestión de historial de conversaciones y generación automática de títulos.

## 📚 Documentación

- **[SECURITY_AUDIT.md](SECURITY_AUDIT.md)** - Auditoría completa de seguridad y calidad de código
- **[RECOMENDACIONES.md](RECOMENDACIONES.md)** - Recomendaciones detalladas de mejoras
- **[CHECKLIST_PRODUCCION.md](CHECKLIST_PRODUCCION.md)** - Checklist para despliegue a producción

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

Este proyecto ha sido auditado para seguridad. Ver [SECURITY_AUDIT.md](SECURITY_AUDIT.md) para detalles completos.

**Puntos importantes:**
- ✅ Sin credenciales hardcodeadas
- ✅ Variables de entorno para configuración sensible
- ✅ .gitignore apropiado
- ⚠️ Leer [CHECKLIST_PRODUCCION.md](CHECKLIST_PRODUCCION.md) antes de desplegar
