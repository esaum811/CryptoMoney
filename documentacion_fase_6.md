# 🚀 Documentación Oficial — Fase 6: Entrega, Despliegue de Valor y Monitoreo (Railway PaaS)

**Proyecto**: Crypto Portfolio Tracker  
**Fase**: 6 — Entrega, Despliegue de Valor en la Nube (Railway), Monitoreo y Salubridad  
**Ubicación del repositorio**: `ProyectoExamen/Crypto-Portfolio-Tracker`  

---

## 1. Resumen Ejecutivo

En la **Fase 6**, la aplicación refactorizada y probada **Crypto Portfolio Tracker** pasó del entorno local a **producción en la nube** mediante la plataforma **Railway PaaS (Platform as a Service)**, conectada directamente al repositorio del proyecto.

Para garantizar el despliegue automático e ininterrumpido en Railway, se adaptó el comando de arranque del servidor WSGI (**Gunicorn**) ajustando el bind del puerto a la variable de entorno asignada dinámicamente por la plataforma (`$PORT`), reemplazando el puerto fijo `5000`.

---

## 2. Cambios Implementados para el Despliegue en Railway

### 2.1 Modificación de Enlace de Puerto Dinámico (`$PORT`)

Railway asigna un puerto aleatorio de forma dinámica al instanciar contenedores en producción. Se adaptaron los artefactos de arranque para capturar la variable de entorno `$PORT`:

1. **Creación de [app.py](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/app.py)**:
   Módulo de entrada directo en la raíz del proyecto para responder a la ejecución de `gunicorn app:app`:
   ```python
   import os
   from app import create_app

   app = create_app()

   if __name__ == '__main__':
       port = int(os.environ.get('PORT', 5000))
       app.run(host='0.0.0.0', port=port, debug=False)
   ```

2. **Actualización de [Dockerfile](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/Dockerfile)**:
   ```dockerfile
   # Comando de inicio usando el servidor WSGI de producción (Gunicorn) escuchando en la variable de entorno PORT (Railway)
   CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000}"]
   ```

3. **Creación del [Procfile](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/Procfile)**:
   ```text
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

4. **Actualización de [docker-compose.yml](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/docker-compose.yml)**:
   ```yaml
   command: sh -c "gunicorn --reload --bind 0.0.0.0:${PORT:-5000} app:app"
   ```

---

## 3. Monitoreo y Diagnóstico de Salud

Se validó el funcionamiento en producción utilizando el endpoint REST `/api/health`:

* **Endpoint**: `GET /api/health`
* **Respuesta Esperada**:
  ```json
  {
    "database": "connected",
    "status": "ok",
    "timestamp": "2026-07-27T18:31:00.000000",
    "version": "2.0.0"
  }
  ```

---

## 4. Entregables Cumplidos de la Fase 6

- [x] Configuración del puerto dinámico `$PORT` en `Dockerfile`, `Procfile` y `docker-compose.yml`.
- [x] Creación del punto de entrada `app.py` compatible con `gunicorn app:app`.
- [x] Preparación del repositorio para el despliegue automático en Railway mediante CI/CD.
- [x] Endpoint de monitoreo y health check activo `/api/health`.
