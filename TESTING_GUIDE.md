# Guía de Testing - Mejoras de Seguridad

Esta guía te ayudará a verificar que todas las mejoras implementadas funcionan correctamente.

---

## 🧪 Tests Manuales Rápidos

### 1. Validación de Input

#### Test 1.1: Mensaje Vacío
```bash
# Ejecutar la aplicación
cd Project
python app.py

# En otro terminal, probar con curl:
curl -X POST http://127.0.0.1:5000/chat/test-id ^
  -H "Content-Type: application/json" ^
  -d "{\"mensaje\": \"   \"}"
```
**Resultado esperado:**
```json
{"error": "Mensaje vacío."}
```
**Status code:** 400

#### Test 1.2: Mensaje Demasiado Largo
```bash
# PowerShell
$longMessage = "a" * 4001
$body = @{mensaje=$longMessage} | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:5000/chat/test-id" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```
**Resultado esperado:**
```json
{"error": "Mensaje demasiado largo. Máximo 4000 caracteres."}
```
**Status code:** 400

#### Test 1.3: Mensaje Válido (debe funcionar)
```bash
curl -X POST http://127.0.0.1:5000/chat/test-id ^
  -H "Content-Type: application/json" ^
  -d "{\"mensaje\": \"Hola, este es un mensaje válido\"}"
```
**Resultado esperado:** Respuesta normal del chat (puede fallar si el chat_id no existe, eso es normal)

---

### 2. Rate Limiting

#### Test 2.1: Rate Limiting en Chat (30 mensajes/minuto)

Crear script de prueba `test_rate_limit.ps1`:

```powershell
# test_rate_limit.ps1
Write-Host "Testing rate limiting (30 requests/minute)..."

# Primero crear un chat
$newChatResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5000/new_chat" `
  -Method POST `
  -ContentType "application/json"
$chatData = $newChatResponse.Content | ConvertFrom-Json
$chatId = $chatData.chat_id

Write-Host "Created chat: $chatId"
Write-Host "Sending 35 rapid requests..."

for ($i = 1; $i -le 35; $i++) {
    try {
        $body = @{mensaje="Test message $i"} | ConvertTo-Json
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/chat/$chatId" `
          -Method POST `
          -ContentType "application/json" `
          -Body $body `
          -ErrorAction Stop
        
        Write-Host "[$i] ✓ Status: $($response.StatusCode)" -ForegroundColor Green
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 429) {
            Write-Host "[$i] ✗ Rate limit exceeded (429)!" -ForegroundColor Red
        } else {
            Write-Host "[$i] ✗ Error: $statusCode" -ForegroundColor Yellow
        }
    }
    
    Start-Sleep -Milliseconds 100
}

Write-Host "`nTest complete! If you saw 429 errors after ~30 requests, rate limiting is working!"
```

Ejecutar:
```powershell
.\test_rate_limit.ps1
```

**Resultado esperado:** 
- Primeros ~30 requests: Status 200 (o 503 si no hay API key)
- Requests 31+: Status 429 (Too Many Requests)

---

### 3. Headers de Seguridad HTTP

#### Test 3.1: Verificar Headers en Producción

**Paso 1:** Configurar modo producción:
```bash
# En .env, cambiar:
FLASK_DEBUG=False
```

**Paso 2:** Ejecutar aplicación:
```bash
python app.py
```

**Paso 3:** Verificar headers:
```powershell
# PowerShell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000" -Method GET
$response.Headers

# Buscar estos headers:
$response.Headers["Strict-Transport-Security"]
$response.Headers["Content-Security-Policy"]
$response.Headers["X-Content-Type-Options"]
$response.Headers["X-Frame-Options"]
```

**Resultado esperado:**
```
Strict-Transport-Security: max-age=...
Content-Security-Policy: default-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
```

#### Test 3.2: Verificar que Talisman NO está activo en desarrollo
```bash
# En .env, cambiar:
FLASK_DEBUG=True
```

Ejecutar y verificar headers nuevamente. **NO deberían aparecer** los headers de Talisman.

---

### 4. CSS con Variables

#### Test 4.1: Verificación Visual

1. **Abrir** http://127.0.0.1:5000 en el navegador
2. **Verificar** que la UI se ve correcta:
   - Colores consistentes
   - Espaciado uniforme
   - Botones bien estilizados
   - Transiciones suaves

3. **Abrir DevTools** (F12) → Console
4. **Ejecutar** este código:
```javascript
// Verificar que las variables CSS están definidas
const root = getComputedStyle(document.documentElement);
console.log("Colores:", {
  primary: root.getPropertyValue('--color-bg-primary'),
  secondary: root.getPropertyValue('--color-bg-secondary'),
  accent: root.getPropertyValue('--color-accent-blue')
});
console.log("Espaciado:", {
  sm: root.getPropertyValue('--spacing-sm'),
  md: root.getPropertyValue('--spacing-md'),
  lg: root.getPropertyValue('--spacing-lg')
});
```

**Resultado esperado:**
```javascript
Colores: {
  primary: "#111827",
  secondary: "#1F2937",
  accent: "#60A5FA"
}
Espaciado: {
  sm: "8px",
  md: "12px",
  lg: "16px"
}
```

#### Test 4.2: Cambio Dinámico de Tema

En la consola del navegador:
```javascript
// Probar cambio de colores
document.documentElement.style.setProperty('--color-accent-blue', '#FF6B6B');
document.documentElement.style.setProperty('--color-accent-green', '#4ECDC4');
```

**Resultado esperado:** Los colores de la UI cambian inmediatamente.

---

## 🔧 Tests Automatizados (Futuro)

Si decides implementar pytest, aquí hay ejemplos de tests:

### Estructura de Tests
```
Project/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_validation.py
│   ├── test_rate_limiting.py
│   └── test_security_headers.py
```

### Ejemplo: test_validation.py
```python
import pytest
from app import app, config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_empty_message_rejected(client):
    """Test que mensajes vacíos son rechazados."""
    response = client.post('/new_chat')
    chat_id = response.get_json()['chat_id']
    
    response = client.post(
        f'/chat/{chat_id}',
        json={'mensaje': '   '}
    )
    assert response.status_code == 400
    assert 'vacío' in response.get_json()['error'].lower()

def test_long_message_rejected(client):
    """Test que mensajes muy largos son rechazados."""
    response = client.post('/new_chat')
    chat_id = response.get_json()['chat_id']
    
    long_message = 'a' * (config.MAX_MESSAGE_LENGTH + 1)
    response = client.post(
        f'/chat/{chat_id}',
        json={'mensaje': long_message}
    )
    assert response.status_code == 400
    assert 'largo' in response.get_json()['error'].lower()

def test_valid_message_accepted(client):
    """Test que mensajes válidos son aceptados."""
    response = client.post('/new_chat')
    chat_id = response.get_json()['chat_id']
    
    response = client.post(
        f'/chat/{chat_id}',
        json={'mensaje': 'Mensaje válido de prueba'}
    )
    # Puede fallar con 503 si no hay API key, pero no con 400
    assert response.status_code != 400
```

### Ejecutar Tests
```bash
# Instalar dependencias de testing
pip install pytest pytest-flask pytest-cov

# Ejecutar todos los tests
pytest

# Ejecutar con coverage
pytest --cov=app --cov-report=html

# Ejecutar tests específicos
pytest tests/test_validation.py -v
```

---

## 📊 Checklist de Verificación Completa

### Funcionalidad Básica
- [ ] La aplicación inicia sin errores
- [ ] Se puede crear un nuevo chat
- [ ] Se pueden enviar mensajes válidos
- [ ] El historial se carga correctamente
- [ ] Se pueden eliminar chats

### Nuevas Características
- [ ] Mensajes vacíos son rechazados (400)
- [ ] Mensajes >4000 chars son rechazados (400)
- [ ] Rate limiting funciona (429 después de 30 requests/min)
- [ ] Headers de seguridad activos en producción (FLASK_DEBUG=False)
- [ ] CSS usa variables (verificado en DevTools)
- [ ] Todas las dependencias instaladas correctamente

### Producción
- [ ] FLASK_DEBUG=False en .env
- [ ] CORS_ORIGINS configurado con dominio específico
- [ ] LOG_LEVEL=WARNING o ERROR
- [ ] API key de OpenAI válida
- [ ] Talisman fuerza HTTPS
- [ ] Rate limits apropiados para tráfico esperado

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'flask_limiter'"
**Solución:**
```bash
pip install Flask-Limiter==3.5.0 flask-talisman==1.1.0
```

### Problema: Rate limiting no funciona
**Causa posible:** Límites muy altos o storage no configurado
**Verificación:**
```python
# En app.py, verificar que exista:
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
```

### Problema: Headers de seguridad no aparecen
**Causa posible:** FLASK_DEBUG=True
**Solución:** Cambiar a `FLASK_DEBUG=False` en `.env`

### Problema: CSS se ve mal
**Causa posible:** Cache del navegador
**Solución:** Ctrl + Shift + R para hard refresh

### Problema: Error 429 inmediatamente
**Causa posible:** Rate limit alcanzado previamente
**Solución:** Reiniciar la aplicación (el storage es en memoria)

---

## 📞 Soporte

Si encuentras problemas:
1. Verificar logs: `Project/logs/app.log`
2. Revisar configuración: `.env` vs `.env.example`
3. Consultar: `PRODUCTION.md` y `MEJORAS_IMPLEMENTADAS.md`

---

**Última actualización:** 21 de Noviembre, 2025
