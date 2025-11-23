# Guía de Configuración para Producción - Project Synapse

Este documento complementa `CHECKLIST_PRODUCCION.md` con guías específicas de configuración segura.

---

## 🔐 Configuración de Seguridad Crítica

### 1. Variables de Entorno

#### ⛔ Configuraciones INSEGURAS (NO usar en producción)

```bash
# ❌ MAL - Permite cualquier origen (vulnerable a CSRF)
CORS_ORIGINS=*

# ❌ MAL - Expone información sensible en errores
FLASK_DEBUG=True

# ❌ MAL - Logs excesivos pueden exponer datos sensibles
LOG_LEVEL=DEBUG
```

#### ✅ Configuraciones SEGURAS (Usar en producción)

```bash
# ✅ BIEN - Dominios específicos únicamente
CORS_ORIGINS=https://tu-dominio.com

# ✅ BIEN - Para múltiples dominios, separar con comas
CORS_ORIGINS=https://app.ejemplo.com,https://www.ejemplo.com

# ✅ BIEN - Debug desactivado
FLASK_DEBUG=False

# ✅ BIEN - Solo logs importantes
LOG_LEVEL=WARNING
# o para producción crítica:
LOG_LEVEL=ERROR
```

### 2. Ejemplo Completo de `.env` para Producción

```bash
# =============================================================================
# PRODUCCIÓN - Synapse AI
# =============================================================================

# API KEY DE OPENAI (REQUERIDO)
OPENAI_APIKEY=sk-proj-tu-api-key-real-de-produccion

# MODELOS DE IA
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TITLE_MODEL=gpt-3.5-turbo

# CONFIGURACIÓN DEL SERVIDOR
FLASK_DEBUG=False
LOG_LEVEL=WARNING
PORT=5000

# CORS - ⚠️ CRÍTICO: Usar dominios específicos
CORS_ORIGINS=https://synapse.tu-dominio.com
```

---

## 🛡️ Características de Seguridad Implementadas

### Rate Limiting

El proyecto incluye rate limiting automático:

- **Global**: 200 requests/día, 50 requests/hora
- **Endpoint de chat**: 30 mensajes/minuto

**Configuración**: Implementado con `Flask-Limiter` en `app.py`

### Validación de Input

Protección contra mensajes maliciosos o excesivos:

- **Mínimo**: 1 carácter
- **Máximo**: 4000 caracteres

Los mensajes fuera de estos límites son rechazados automáticamente.

### Headers de Seguridad HTTP

Cuando `FLASK_DEBUG=False`, se activan automáticamente:

- Content Security Policy (CSP)
- HTTPS forzado
- Protección contra clickjacking
- Prevención de MIME sniffing

**Implementado con**: `Flask-Talisman`

---

## 🚀 Pasos para Despliegue Seguro

### Paso 1: Preparar el Entorno

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Project-Synapse.git
cd Project-Synapse

# 2. Crear entorno virtual
python -m venv venv

# Linux/Mac
source venv/bin/activate
# Windows
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r Project/requirements.txt
```

### Paso 2: Configurar Variables de Entorno

```bash
# 1. Copiar plantilla
cp Project/.env.example Project/.env

# 2. Editar .env con valores de producción
# Usar un editor de texto o:
nano Project/.env  # Linux/Mac
notepad Project/.env  # Windows
```

**⚠️ IMPORTANTE**: Verificar que:
- `FLASK_DEBUG=False`
- `CORS_ORIGINS` tiene tu dominio específico
- `LOG_LEVEL=WARNING` o `ERROR`
- API key es válida y de producción

### Paso 3: Verificar Configuración

Antes de desplegar, ejecutar verificación:

```bash
cd Project
python -c "from app import config; print(f'DEBUG: {config.FLASK_DEBUG}'); print(f'CORS: {config.CORS_ORIGINS}'); print(f'LOG: {config.LOG_LEVEL}')"
```

**Salida esperada**:
```
DEBUG: False
CORS: https://tu-dominio.com
LOG: WARNING
```

### Paso 4: Configurar Servidor Web

#### Opción A: Usando Gunicorn (Recomendado para Linux)

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar con 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Opción B: Usando Waitress (Recomendado para Windows)

```bash
# Instalar waitress
pip install waitress

# Ejecutar
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Paso 5: Configurar Nginx como Proxy Reverso

Crear archivo de configuración `/etc/nginx/sites-available/synapse`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    # Redirigir todo a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    # Certificados SSL
    ssl_certificate /ruta/a/tu/certificado.crt;
    ssl_certificate_key /ruta/a/tu/clave.key;
    
    # Configuración SSL segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Logs
    access_log /var/log/nginx/synapse_access.log;
    error_log /var/log/nginx/synapse_error.log;
    
    # Proxy a la aplicación Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Archivos estáticos (opcional, mejora performance)
    location /static {
        alias /ruta/a/Project-Synapse/Project/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Activar configuración:

```bash
sudo ln -s /etc/nginx/sites-available/synapse /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl reload nginx
```

### Paso 6: Configurar Systemd (Auto-inicio)

Crear archivo `/etc/systemd/system/synapse.service`:

```ini
[Unit]
Description=Synapse AI Application
After=network.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/ruta/a/Project-Synapse/Project
Environment="PATH=/ruta/a/Project-Synapse/venv/bin"
ExecStart=/ruta/a/Project-Synapse/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable synapse
sudo systemctl start synapse
sudo systemctl status synapse
```

---

## 🔍 Verificación Post-Despliegue

### Checklist de Verificación

- [ ] Aplicación responde en HTTPS
- [ ] HTTP redirige a HTTPS
- [ ] CORS solo permite tu dominio
- [ ] Rate limiting funciona (probar 31+ mensajes/minuto)
- [ ] Validación de mensajes largos funciona (>4000 chars)
- [ ] Logs se están generando correctamente
- [ ] No hay errores en `/Project/logs/app.log`

### Pruebas de Seguridad

```bash
# 1. Verificar headers de seguridad
curl -I https://tu-dominio.com

# Buscar estos headers:
# - Strict-Transport-Security
# - Content-Security-Policy
# - X-Content-Type-Options
# - X-Frame-Options

# 2. Probar CORS (desde otro dominio)
curl -H "Origin: https://sitio-malicioso.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://tu-dominio.com/chat/test-id

# Debería rechazar o no incluir Access-Control-Allow-Origin

# 3. Probar rate limiting
# Ejecutar este script 35 veces rápidamente
for i in {1..35}; do
  curl -X POST https://tu-dominio.com/chat/test-id \
       -H "Content-Type: application/json" \
       -d '{"mensaje":"test"}'
done
# Debería empezar a rechazar después de 30 requests
```

---

## 📊 Monitoreo

### Logs a Revisar Regularmente

```bash
# Logs de la aplicación
tail -f /ruta/a/Project-Synapse/Project/logs/app.log

# Logs de Nginx
tail -f /var/log/nginx/synapse_error.log
tail -f /var/log/nginx/synapse_access.log

# Logs del sistema
sudo journalctl -u synapse -f
```

### Métricas Importantes

- **Errores 500**: No deberían ocurrir en operación normal
- **Errores 429**: Indica rate limiting activo (normal si hay abuso)
- **Errores 400**: Usuarios intentando enviar mensajes inválidos
- **Uso de disco**: `/Project/chats` y `/Project/logs` crecen con el tiempo

---

## 🆘 Troubleshooting

### Problema: Rate Limiting muy agresivo

**Solución**: Ajustar límites en `app.py`:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],  # Aumentado
    storage_uri="memory://"
)

@app.route("/chat/<chat_id>", methods=["POST"])
@limiter.limit("60 per minute")  # Aumentado
```

### Problema: CSP bloquea recursos

**Síntoma**: Consola del browser muestra errores CSP

**Solución**: Agregar dominios a la configuración de Talisman en `app.py`:

```python
'script-src': [
    "'self'",
    "'unsafe-inline'",
    'https://cdn.jsdelivr.net',
    'https://unpkg.com',
    'https://tu-nuevo-cdn.com'  # Agregar aquí
],
```

### Problema: Error 502 Bad Gateway

**Causas comunes**:
1. Aplicación Flask no está corriendo
2. Puerto incorrecto en nginx
3. Firewall bloqueando conexión

**Verificación**:

```bash
# ¿Está corriendo la aplicación?
sudo systemctl status synapse

# ¿Responde en el puerto local?
curl http://127.0.0.1:5000

# ¿Nginx puede conectarse?
sudo nginx -t
sudo systemctl status nginx
```

---

## 🔄 Actualizaciones

### Proceso de Actualización Seguro

```bash
# 1. Backup de datos
cp -r /ruta/a/Project-Synapse/Project/chats /backup/chats_$(date +%Y%m%d)

# 2. Detener servicio
sudo systemctl stop synapse

# 3. Actualizar código
cd /ruta/a/Project-Synapse
git pull origin main

# 4. Actualizar dependencias
source venv/bin/activate
pip install -r Project/requirements.txt --upgrade

# 5. Reiniciar servicio
sudo systemctl start synapse

# 6. Verificar logs
sudo journalctl -u synapse -f
```

---

## 📞 Contactos de Emergencia

**Proveedor de Hosting**:
- Soporte: _________________
- Panel: _________________

**OpenAI**:
- Portal: https://platform.openai.com/
- Soporte: https://help.openai.com/

**DNS/Dominio**:
- Proveedor: _________________
- Panel: _________________

---

## 📚 Referencias

- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Observatory](https://observatory.mozilla.org/) - Para verificar seguridad de tu sitio
- [SSL Labs](https://www.ssllabs.com/ssltest/) - Para verificar configuración SSL

---

**Última actualización**: 21 de Noviembre, 2025

Para información adicional, consultar:
- `CHECKLIST_PRODUCCION.md` - Checklist detallado pre-despliegue
- `SECURITY_AUDIT.md` - Auditoría completa de seguridad
- `RECOMENDACIONES.md` - Mejoras adicionales sugeridas
