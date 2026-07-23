# 📗 Documentación Oficial — Fase 2: Inmutabilidad, Contenedorización Local (Docker) y Buenas Prácticas

**Proyecto**: Crypto Portfolio Tracker  
**Fase**: 2 — Inmutabilidad, Contenedorización Local (Docker), Hot Reload y Aplicación de Buenas Prácticas  
**Ubicación del repositorio**: `ProyectoExamen/Crypto-Portfolio-Tracker`  

---

## 1. Resumen de la Fase 2

En la **Fase 2**, se garantizó la **portabilidad, inmutabilidad y aislamiento** de la aplicación **Crypto Portfolio Tracker** mediante la creación de imágenes y contenedores Docker optimizados. Además, se implementó el soporte para **Hot Reload (recarga en tiempo real)** mediante volúmenes en entornos de desarrollo y se aplicó la regla fundamental de **buenas prácticas de programación** documentando todo el código fuente con comentarios y docstrings bajo el estándar **PEP 8**.

---

## 2. Componentes e Infraestructura de la Fase 2

### 2.1 Archivo Dockerfile Optimizado ([Dockerfile](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/Dockerfile))
Se construyó una imagen multi-capa basada en una versión ligera de Python:

* **Imagen Base**: `python:3.11-slim` para minimizar el tamaño del contenedor y vulnerabilidades.
* **Variables de Entorno**:
  * `PYTHONDONTWRITEBYTECODE=1`: Evita la creación de archivos `.pyc` dentro del contenedor.
  * `PYTHONUNBUFFERED=1`: Asegura que los logs de la aplicación se transmitan inmediatamente a la consola (`stdout`/`stderr`).
* **Optimización de Capas de Caché**:
  * Separación del comando `COPY requirements.txt` del código fuente para reutilizar las capas de instalación de paquetes de `pip`.
  * Instalación con la bandera `--no-cache-dir`.
* **Servidor WSGI de Producción**:
  * Reemplazo de `flask run` (servidor de desarrollo no apto para producción) por **Gunicorn** escuchando en el puerto `5000` (`CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]`).

### 2.2 Archivo `.dockerignore` ([.dockerignore](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/.dockerignore))
Se configuró para ignorar elementos no deseados, reduciendo el tamaño del contexto de build:
* Archivos de control de versiones (`.git`, `.gitignore`).
* Entornos virtuales de Python (`.venv/`, `venv/`, `env/`).
* Archivos de caché y bytecode (`__pycache__/`, `*.pyc`, `.pytest_cache/`).
* Variables de entorno locales y secretos (`.env`).
* Archivos de base de datos local e instancias (`*.db`, `crypto.db`, `instance/`).

### 2.3 Orquestación con Hot Reload ([docker-compose.yml](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/docker-compose.yml))
Para cumplir con el requerimiento de desarrollo local dinámico, se creó un archivo `docker-compose.yml` que habilita **Hot Reload**:
* **Montaje de Volumen**: `- .:/app` enlaza la carpeta raíz del proyecto local con el directorio de trabajo del contenedor.
* **Reloader de Gunicorn**: Se ejecuta el comando `gunicorn --reload --bind 0.0.0.0:5000 run:app`, el cual monitorea en tiempo real los cambios en los archivos `.py` y reinicia automáticamente los procesos trabajadores sin necesidad de reconstruir la imagen Docker.

---

## 3. Problemas Identificados y Soluciones Aplicadas en la Fase 2

| # | Problema Detectado | Impacto | Solución Aplicada en Fase 2 |
|---|--------------------|---------|-----------------------------|
| **1** | **Código sin Documentación Ni Docstrings** | Dificultad para mantener y entender la intención de las funciones y clases refactorizadas. | Adición sistemática de docstrings PEP 8 y comentarios concisos en los 12 archivos Python principales del proyecto. |
| **2** | **Dockerfile Legacy Ineficiente** | Usaba `python:3.10.7-slim-buster`, `flask run` en modo desarrollo y no optimizaba el caché de paquetes. | Migración a `python:3.11-slim`, uso de `Gunicorn` WSGI y banderas `--no-cache-dir`. |
| **3** | **Falta de `.dockerignore`** | La imagen compilaba incluyendo bases de datos SQLite locales (`crypto.db`), `.git` y entornos virtuales pesados. | Creación de [.dockerignore](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/.dockerignore) excluyendo archivos temporales y datos sensibles. |
| **4** | **Código Estático en el Contenedor** | Modificar un archivo local exigía destruir el contenedor y re-ejecutar `docker build` manualmente. | Configuración de `docker-compose.yml` con **montaje de volumen** (`.:/app`) y la opción `--reload` para desarrollo local en vivo. |
| **5** | **Demonio de Docker Detenido en Windows** | El comando `docker build` fallaba por falta de conexión al socket `npipe:////./pipe/dockerDesktopLinuxEngine`. | Automatización del arranque del proceso `Docker Desktop.exe` y verificación con `docker info` previo al despliegue. |

---

## 4. Verificación y Evidencia de Funcionamiento

1. **Validación de Sintaxis Python**:
   ```bash
   python -m py_compile run.py config.py app/__init__.py app/models.py app/extensions.py app/tasks.py app/auth/forms.py app/auth/routes.py app/main/forms.py app/main/routes.py app/services/bybit_client.py app/services/email_service.py
   ```
   *Resultado*: 100% de archivos validados sin errores de sintaxis.

2. **Compilación y Despliegue con Docker Compose**:
   ```bash
   docker compose up -d
   ```
   *Resultado*: Contenedor `crypto-app` en estado `Up (running)` sirviendo en `http://localhost:5000`.

3. **Verificación de Logs del Reloader**:
   ```text
   [INFO] Starting gunicorn 26.0.0
   [INFO] Listening at: http://0.0.0.0:5000 (1)
   [WARNING] Reloader is on. Use in development only!
   ```

4. **Respuesta del Endpoint de Diagnóstico `/api/health`**:
   ```json
   {
     "database": "connected",
     "status": "ok",
     "timestamp": "2026-07-23T05:32:05.564458",
     "version": "2.0.0"
   }
   ```

---

## 5. Entregables Cumplidos de la Fase 2

- [x] Código Python 100% comentado y documentado con docstrings PEP 8.
- [x] Archivo `Dockerfile` optimizado en la raíz del proyecto.
- [x] Archivo `.dockerignore` configurado.
- [x] Archivo `docker-compose.yml` configurado con Hot Reload mediante volúmenes.
- [x] Evidencia de compilación y ejecución de contenedor aislado respondiendo en el puerto 5000.
