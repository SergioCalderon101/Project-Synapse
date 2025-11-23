# Guía de Despliegue a Producción - Synapse AI

Esta guía proporciona un checklist completo y procedimientos detallados para desplegar Synapse AI de forma segura en producción.

---

## 📋 Checklist Pre-Despliegue

### ⚙️ Variables de Entorno

#### Archivo `.env` Requerido

- [ ] **OPENAI_APIKEY** configurada con API key válida de producción
- [ ] **OPENAI_CHAT_MODEL** configurado (`gpt-4o-mini` recomendado)
- [ ] **OPENAI_TITLE_MODEL** configurado (o usar default)
- [ ] **FLASK_DEBUG** = `False` ⚠️ **CRÍTICO**
- [ ] **LOG_LEVEL** = `WARNING` o `ERROR` (no `DEBUG`)
- [ ] **PORT** configurado según infraestructura
- [ ] **CORS_ORIGINS** = dominios específicos, **NO usar `*`** ⚠️ **CRÍTICO**

#### ⛔ Configuraciones INSEGURAS (NO usar)

```bash
# ❌ MAL - Permite cualquier origen (vulnerable a CSRF)
CORS_ORIGINS=*

# ❌ MAL - Expone información sensible en errores
FLASK_DEBUG=True

# ❌ MAL - Logs excesivos pueden exponer datos
LOG_LEVEL=DEBUG
```

#### ✅ Ejemplo de `.env` para Producción

```bash
# API KEY DE OPENAI
OPENAI_APIKEY=sk-proj-tu-api-key-real-de-produccion

# MODELOS DE IA
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TITLE_MODEL=gpt-3.5-turbo

# CONFIGURACIÓN DEL SERVIDOR
FLASK_DEBUG=False
LOG_LEVEL=WARNING
PORT=5000

# CORS - Dominios específicos únicamente
CORS_ORIGINS=https://tu-dominio.com
# Para múltiples dominios:
# CORS_ORIGINS=https://app.ejemplo.com,https://www.ejemplo.com
```

---

### 🔐 Seguridad

#### Crítico

- [ ] API keys rotadas desde desarrollo/testing
- [ ] `.env` nunca subido a GitHub (verificar con `git log`)
- [ ] CORS configurado con dominios específicos
- [ ] `FLASK_DEBUG=False` en producción
- [ ] HTTPS configurado y forzado
- [ ] Firewall configurado (solo puertos necesarios)

#### Recomendado

- [ ] Rate limiting verificado (incluido por defecto)
- [ ] Headers de seguridad HTTP activos (incluido por defecto)
- [ ] Validación de longitud de mensajes activa (1-4000 caracteres)
- [ ] Logs sensibles removidos o enmascarados

**Características de Seguridad Incluidas:**

- **Rate Limiting**: 200 req/día, 50 req/hora (global), 30 msg/min (chat)
- **Validación de Input**: 1-4000 caracteres por mensaje
- **Headers de Seguridad**: CSP, HSTS, X-Frame-Options, etc. (auto-activados cuando `FLASK_DEBUG=False`)

---

### 🗄️ Datos y Persistencia

- [ ] Directorio `/chats` tiene permisos correctos
- [ ] Directorio `/logs` tiene permisos correctos
- [ ] Sistema de backups configurado para `/chats`
- [ ] Política de retención de logs definida
- [ ] Espacio en disco monitoreado

---

### 📊 Monitoreo

#### Básico (Mínimo)

- [ ] Logs agregados y revisables
- [ ] Alertas configuradas para errores 500
- [ ] Monitoreo de uso de disco
- [ ] Monitoreo de memoria

#### Recomendado

- [ ] Servicio de error tracking (Sentry u otro)
- [ ] Métricas de performance monitoreadas
- [ ] Uptime monitoring configurado
- [ ] Dashboard de métricas

---

### 🧪 Testing

- [ ] Tests básicos ejecutados y pasando
- [ ] Test de carga realizado (si aplica)
- [ ] Validación de endpoints críticos
- [ ] Verificación de manejo de errores

---

### 📚 Documentación

- [ ] README actualizado
- [ ] Variables de entorno documentadas
- [ ] Proceso de backup documentado
- [ ] Contactos de emergencia definidos
- [ ] Runbook para incidentes comunes

---

### 🚀 Despliegue

#### Pre-Despliegue

- [ ] Código en rama estable (`main`/`production`)
- [ ] Versión taggeada en git
- [ ] Dependencias actualizadas y sin vulnerabilidades
- [ ] Build exitoso localmente

#### Durante Despliegue

- [ ] Variables de entorno configuradas en servidor
- [ ] Servicio web configurado (nginx/apache)
- [ ] Procesos supervisados (systemd/supervisor)
- [ ] SSL/TLS certificados instalados

#### Post-Despliegue

- [ ] Aplicación accesible vía HTTPS
- [ ] Logs monitoreados (primeros 30 min)
- [ ] Prueba de funcionalidad básica realizada
- [ ] Backups verificados
- [ ] Rollback plan listo

---

### ⚡ Performance

- [ ] Timeout de requests configurado
- [ ] Límites de concurrencia configurados
- [ ] Recursos del servidor adecuados (CPU, RAM)
- [ ] CDN para assets estáticos (opcional)

---

### 🔄 Mantenimiento

#### Rutinas Planificadas

- [ ] Plan de actualización de dependencias
- [ ] Rotación de API keys programada
- [ ] Revisión de logs periódica
- [ ] Limpieza de datos antiguos automatizada

---

## 🛠️ Procedimientos Detallados

### Paso 1: Preparar el Entorno

```bash
# 1. Clonar el repositorio
git clone https://github.com/SergioCalderon101/Project-Synapse.git
cd Project-Synapse

# 2. Crear entorno virtual
python -m venv venv

# Linux/Mac
source venv/bin/activate
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias
pip install -r Project/requirements.txt
```

### Paso 2: Configurar Variables de Entorno

```bash
# 1. Copiar plantilla
cp Project/.env.example Project/.env

# 2. Editar con valores de producción
# Linux/Mac
nano Project/.env
# Windows
notepad Project/.env
```

**⚠️ VERIFICAR:**
- `FLASK_DEBUG=False`
- `CORS_ORIGINS` con tu dominio específico
- `LOG_LEVEL=WARNING` o `ERROR`
- API key válida y de producción

### Paso 3: Verificar Configuración

```bash
cd Project
python -c "from app import config; print(f'DEBUG: {config.FLASK_DEBUG}'); print(f'CORS: {config.CORS_ORIGINS}'); print(f'LOG: {config.LOG_LEVEL}')"
```

**Salida esperada:**
```
DEBUG: False
CORS: https://tu-dominio.com
LOG: WARNING
```

### Paso 4: Configurar Servidor de Aplicación

#### Opción A: Gunicorn (Recomendado para Linux)

```bash
# Instalar
pip install gunicorn

# Ejecutar con 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Opción B: Waitress (Recomendado para Windows)

```bash
# Instalar
pip install waitress

# Ejecutar
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Paso 5: Configurar Nginx (Proxy Reverso)

Crear `/etc/nginx/sites-available/synapse`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;
    
    # Certificados SSL
    ssl_certificate /ruta/a/certificado.crt;
    ssl_certificate_key /ruta/a/clave.key;
    
    # Configuración SSL segura
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Logs
    access_log /var/log/nginx/synapse_access.log;
    error_log /var/log/nginx/synapse_error.log;
    
    # Proxy a Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Archivos estáticos (mejora performance)
    location /static {
        alias /ruta/a/Project-Synapse/Project/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Activar:

```bash
sudo ln -s /etc/nginx/sites-available/synapse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Paso 6: Configurar Systemd (Auto-inicio en Linux)

Crear `/etc/systemd/system/synapse.service`:

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

Activar:

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
- [ ] HTTP redirige a HTTPS automáticamente
- [ ] CORS solo permite dominios configurados
- [ ] Rate limiting funciona (probar 31+ mensajes/minuto)
- [ ] Validación de mensajes largos funciona (>4000 caracteres)
- [ ] Logs se generan correctamente
- [ ] No hay errores en `/Project/logs/app.log`

### Pruebas de Seguridad

```bash
# 1. Verificar headers de seguridad
curl -I https://tu-dominio.com

# Buscar:
# - Strict-Transport-Security
# - Content-Security-Policy
# - X-Content-Type-Options
# - X-Frame-Options

# 2. Probar CORS (desde origen no autorizado)
curl -H "Origin: https://sitio-malicioso.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://tu-dominio.com/chat/test-id
# Debería rechazar o no incluir Access-Control-Allow-Origin

# 3. Probar rate limiting
for i in {1..35}; do
  curl -X POST https://tu-dominio.com/chat/test-id \
       -H "Content-Type: application/json" \
       -d '{"mensaje":"test"}'
done
# Debería empezar a rechazar después de ~30 requests
```

---

## 📊 Monitoreo y Logs

### Revisar Logs Regularmente

```bash
# Logs de la aplicación
tail -f /ruta/a/Project-Synapse/Project/logs/app.log

# Logs de Nginx (Linux)
tail -f /var/log/nginx/synapse_error.log
tail -f /var/log/nginx/synapse_access.log

# Logs del sistema (systemd)
sudo journalctl -u synapse -f
```

### Métricas Importantes

- **Errores 500**: No deberían ocurrir en operación normal
- **Errores 429**: Rate limiting activo (normal si hay abuso)
- **Errores 400**: Mensajes inválidos de usuarios
- **Uso de disco**: `/Project/chats` y `/Project/logs` crecen con el tiempo

---

## 🆘 Troubleshooting

### Problema: Rate Limiting muy Agresivo

Ajustar límites en `app.py`:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],  # Aumentado
    storage_uri="memory://"
)

@app.route("/chat/<chat_id>", methods=["POST"])
@limiter.limit("60 per minute")  # Aumentado de 30 a 60
```

### Problema: CSP Bloquea Recursos

Si la consola del browser muestra errores CSP, agregar dominios en `app.py`:

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

**Causas comunes:**
1. Aplicación Flask no está corriendo
2. Puerto incorrecto en nginx
3. Firewall bloqueando conexión

**Verificación:**

```bash
# ¿Está corriendo?
sudo systemctl status synapse

# ¿Responde localmente?
curl http://127.0.0.1:5000

# ¿Nginx está OK?
sudo nginx -t
sudo systemctl status nginx
```

### Problema: Aplicación No Responde

```bash
# Verificar logs
tail -f Project/logs/app.log

# Verificar proceso
ps aux | grep python

# Verificar puerto
netstat -tulpn | grep 5000  # Linux
netstat -ano | findstr :5000  # Windows

# Reiniciar servicio (Linux)
sudo systemctl restart synapse
```

### Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| Errores 500 frecuentes | Verificar conectividad OpenAI | Revisar logs, verificar API key |
| Alto uso de API OpenAI | Posible abuso | Verificar rate limiting, rotar API key |
| Disco lleno | `/chats` o `/logs` creciendo | Implementar limpieza automática |
| Aplicación lenta | Falta de recursos | Aumentar workers de Gunicorn/Waitress |

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

## 📱 Contactos de Emergencia

**Desarrollador Principal:**
- Nombre: ___________________
- Email: ___________________
- Teléfono: ___________________

**DevOps/SysAdmin:**
- Nombre: ___________________
- Email: ___________________
- Teléfono: ___________________

**Proveedores:**
- **OpenAI**: https://platform.openai.com/ | https://help.openai.com/
- **Hosting**: ___________________ | Panel: ___________________
- **DNS/Dominio**: ___________________ | Panel: ___________________

---

## 📝 Registro de Despliegue

**Fecha:** _______________  
**Versión:** _______________  
**Desplegado por:** _______________  
**Entorno:** ☐ Staging  ☐ Production

**Notas:**
```
(Agregar observaciones relevantes de este despliegue)
```

---

## ✅ Checklist Final

Antes de marcar como "Listo para Producción":

- [ ] **Todos los items críticos** completados
- [ ] **Al menos 80%** de items recomendados completados
- [ ] **Smoke tests** exitosos
- [ ] **Equipo notificado** del despliegue
- [ ] **Documentación actualizada**
- [ ] **Plan de rollback** documentado
- [ ] **Monitoreo activo** configurado

---

## 🆘 Runbook de Emergencias

### Emergencia: Aplicación Caída

1. Verificar logs: `tail -f Project/logs/app.log`
2. Verificar proceso: `ps aux | grep python`
3. Verificar puerto: `netstat -tulpn | grep 5000`
4. Reiniciar: `sudo systemctl restart synapse`
5. Si persiste, verificar `.env` y permisos

### Emergencia: API OpenAI Comprometida

1. Rotar API key inmediatamente en https://platform.openai.com/
2. Actualizar `.env` con nueva key
3. Reiniciar aplicación: `sudo systemctl restart synapse`
4. Revisar logs de uso anormal
5. Contactar soporte OpenAI si es necesario

### Emergencia: Alto Tráfico/Abuso

1. Verificar rate limiting activo
2. Revisar logs para identificar IPs problemáticas
3. Configurar firewall para bloquear IPs si necesario
4. Considerar reducir límites temporalmente
5. Monitorear costos de API OpenAI

---

## 📚 Referencias

- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mozilla Observatory](https://observatory.mozilla.org/) - Verificar seguridad del sitio
- [SSL Labs](https://www.ssllabs.com/ssltest/) - Verificar configuración SSL
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

**Última actualización:** 22 de Noviembre, 2025  
**Versión del documento:** 1.0

Para más información, consultar `README.md` en el repositorio.
