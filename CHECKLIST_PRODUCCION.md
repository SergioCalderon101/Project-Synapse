# Checklist de Producción - Project Synapse

Use este checklist antes de desplegar a producción.

---

## ⚙️ Configuración de Variables de Entorno

### Archivo .env

- [ ] **OPENAI_APIKEY** está configurada con una API key válida de OpenAI
- [ ] **OPENAI_CHAT_MODEL** configurado al modelo deseado
- [ ] **OPENAI_TITLE_MODEL** configurado (o usar el default)
- [ ] **FLASK_DEBUG** = `False` (⚠️ CRÍTICO)
- [ ] **LOG_LEVEL** = `WARNING` o `ERROR` (no `DEBUG`)
- [ ] **PORT** configurado según tu infraestructura
- [ ] **CORS_ORIGINS** = dominios específicos, NO usar `*` (⚠️ CRÍTICO)

### Ejemplo de .env para Producción:
```bash
OPENAI_APIKEY=sk-proj-tu-api-key-real-aqui
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TITLE_MODEL=gpt-3.5-turbo
FLASK_DEBUG=False
LOG_LEVEL=WARNING
PORT=5000
CORS_ORIGINS=https://tu-dominio.com
```

---

## 🔐 Seguridad

### Crítico
- [ ] API keys rotadas desde desarrollo/testing
- [ ] .env nunca subido a GitHub (verificar con git log)
- [ ] CORS configurado con dominios específicos
- [ ] FLASK_DEBUG=False en producción
- [ ] HTTPS configurado y forzado
- [ ] Firewall configurado para permitir solo puertos necesarios

### Recomendado
- [ ] Rate limiting implementado (ver RECOMENDACIONES.md)
- [ ] Headers de seguridad HTTP configurados
- [ ] Validación de longitud de input implementada
- [ ] Logs sensibles removidos o enmascarados

---

## 🗄️ Datos y Persistencia

- [ ] Directorio `/chats` tiene permisos correctos
- [ ] Directorio `/logs` tiene permisos correctos
- [ ] Sistema de backups configurado para `/chats`
- [ ] Política de retención de logs definida
- [ ] Espacio en disco monitoreado

---

## 📊 Monitoreo

### Básico (Mínimo)
- [ ] Logs agregados y revisables
- [ ] Alertas configuradas para errores 500
- [ ] Monitoreo de uso de disco
- [ ] Monitoreo de memoria

### Recomendado
- [ ] Sentry u otro servicio de error tracking configurado
- [ ] Métricas de performance monitoreadas
- [ ] Uptime monitoring configurado
- [ ] Dashboard de métricas implementado

---

## 🧪 Testing

- [ ] Tests básicos ejecutados y pasando
- [ ] Test de carga realizado (si aplica)
- [ ] Validación de endpoints críticos
- [ ] Verificación de manejo de errores

---

## 📚 Documentación

- [ ] README actualizado con instrucciones de despliegue
- [ ] Variables de entorno documentadas
- [ ] Proceso de backup documentado
- [ ] Contactos de emergencia documentados
- [ ] Runbook para incidentes comunes

---

## 🚀 Despliegue

### Pre-Despliegue
- [ ] Código en rama estable (main/production)
- [ ] Versión taggeada en git
- [ ] Dependencias actualizadas y sin vulnerabilidades
- [ ] Build/compile exitoso

### Despliegue
- [ ] Variables de entorno configuradas en servidor
- [ ] Servicio web configurado (nginx/apache)
- [ ] Procesos supervisados (systemd/supervisor)
- [ ] SSL/TLS certificados instalados

### Post-Despliegue
- [ ] Aplicación accesible vía HTTPS
- [ ] Logs monitoreados por primeros 30 minutos
- [ ] Prueba de funcionalidad básica realizada
- [ ] Backups verificados
- [ ] Rollback plan listo

---

## ⚡ Performance

- [ ] Timeout de requests configurado
- [ ] Límites de concurrencia configurados
- [ ] Recursos del servidor adecuados (CPU, RAM)
- [ ] CDN configurado para assets estáticos (opcional)

---

## 🔄 Mantenimiento

### Rutinas
- [ ] Plan de actualización de dependencias definido
- [ ] Rotación de API keys planificada
- [ ] Revisión de logs programada
- [ ] Limpieza de datos antiguos automatizada

---

## 📱 Contactos de Emergencia

Completar antes del despliegue:

**Desarrollador Principal:**
- Nombre: ___________________
- Email: ___________________
- Teléfono: ___________________

**DevOps/SysAdmin:**
- Nombre: ___________________
- Email: ___________________
- Teléfono: ___________________

**Proveedor OpenAI:**
- Portal: https://platform.openai.com/
- Support: https://help.openai.com/

---

## ✅ Checklist Final

Antes de marcar como "Listo para Producción":

- [ ] Todos los items críticos completados
- [ ] Al menos 80% de items recomendados completados
- [ ] Pruebas de smoke test exitosas
- [ ] Equipo notificado del despliegue
- [ ] Documentación actualizada
- [ ] Plan de rollback documentado

---

## 📝 Notas de Despliegue

**Fecha de Despliegue:** _______________  
**Versión:** _______________  
**Desplegado por:** _______________

**Notas adicionales:**
```
(Agregar cualquier nota relevante sobre este despliegue específico)
```

---

## 🆘 En Caso de Emergencia

### La aplicación no responde:
1. Verificar logs: `tail -f Project/logs/app.log`
2. Verificar proceso: `ps aux | grep python`
3. Verificar puerto: `netstat -tulpn | grep 5000`
4. Reiniciar servicio

### Errores 500 frecuentes:
1. Revisar logs de errores
2. Verificar conectividad a OpenAI API
3. Verificar API key válida
4. Verificar espacio en disco

### Alto uso de API OpenAI:
1. Verificar rate limiting activo
2. Revisar logs de uso anormal
3. Rotar API key si hay sospecha de compromiso
4. Contactar soporte de OpenAI

---

**Última actualización:** 21 de Noviembre, 2025

Para más detalles, consultar:
- `SECURITY_AUDIT.md` - Análisis completo de seguridad
- `RECOMENDACIONES.md` - Mejoras recomendadas
- `README.md` - Documentación general
