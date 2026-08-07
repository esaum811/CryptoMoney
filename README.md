# 🚀 Crypto Portfolio Tracker (Proyecto de Reingeniería)

> ⚠️ **AVISO**: Este repositorio representa la **Reingeniería de Software** del sistema *Crypto Portfolio Tracker*, habiendo sido transformado desde un prototipo monolítico simple hacia una plataforma web moderna, modular, bilingüe (Español/Inglés), contenedorizada en Docker y desplegada en producción.

[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://cryptomoney-production.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-24%2F24%20Passed%20(100%25)-00C853?style=for-the-badge&logo=pytest&logoColor=white)](#-suite-de-pruebas)

---

## 🌐 Despliegue en Producción

El proyecto reingenierizado se encuentra desplegado y activo en la nube a través de **Railway PaaS**:

👉 **URL de la Aplicación**: [https://cryptomoney-production.up.railway.app](https://cryptomoney-production.up.railway.app)  
👉 **Endpoint de Diagnóstico y Salud**: [https://cryptomoney-production.up.railway.app/api/health](https://cryptomoney-production.up.railway.app/api/health)

---

## 📜 Estado Antiguo del Proyecto (Antes de la Reingeniería)

### Estructura y Lenguajes Originales
En su versión inicial, el sistema era un script script monolítico con una estructura básica:
- **Lenguaje Principal**: Python con un único archivo script de Flask sin patrones de diseño (Application Factory no implementado).
- **Frontend**: Plantillas HTML básicas con Bootstrap por defecto sin soporte para temas dinámicos ni personalización avanzada.
- **Internacionalización**: Texto rígido en inglés sin diccionarios de traducción ni localización cliente.
- **Gráficos**: Integración elemental de Plotly en inglés con tooltips por defecto sin traducir.
- **Despliegue**: Sin contenedorización de Docker ni pipelines de integración continua CI/CD.

```
Estructura Antigua (Monolítica):
app.py (script único con rutas, base de datos y lógica mezclada)
templates/ (plantillas HTML sin modularidad)
static/ (CSS/JS básicos sin localización)
```

---

## 🔄 Cambios y Mejoras de Reingeniería Realizados

Durante la fase de Reingeniería de Software se realizaron las siguientes transformaciones principales:

### 1. Refactorización Arquitectónica
- Implementación del patrón **Application Factory Pattern** (`create_app()`) con separación en **Blueprints de Flask** (`auth` y `main`).
- Creación de un módulo de servicios aislados (`services/bybit_client.py` y `services/email_service.py`) con resiliencia y fallbacks automáticos entre Bybit, Binance y Coinbase API.

### 2. Sistema de Internacionalización Bilingüe (i18n Español / Inglés)
- Integración de **Flask-Babel** combinada con un diccionario dinámico `SPANISH_TRANSLATIONS` en Jinja2.
- Localización cliente completa en JavaScript incluyendo la registración del catálogo en español de **Plotly.js** (`Plotly.register`) para los tooltips de la barra de herramientas.
- Persistencia de preferencia de idioma mediante cookies HTTP y sesión.

### 3. Rediseño de UI/UX y Soporte Dual (Modo Claro / Modo Oscuro)
- **Pantalla de Login (`login.html`)**: Rediseño en 2 columnas con tarjeta independiente, textos de marca por encima de la ilustración y una imagen personalizada estilo caricatura sin marco ([crypto_cartoon_swap.png](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/app/static/crypto_cartoon_swap.png)).
- **Pantalla de Registro (`signup.html`)**: Optimización de dimensiones y eliminación de desbordamientos verticales.
- **Adaptabilidad a Modo Claro**: En modo claro (`data-bs-theme="light"`), las tarjetas cambian automáticamente a **blanco puro (`#ffffff`)** con textos oscuros de alto contraste (`#1e2022`).
- **Limpieza de Pantalla**: Eliminación de la barra lateral divisoria en vistas no autenticadas (`base.html`).

### 4. Contenedorización & Pruebas Automáticas
- Creación de `Dockerfile` multi-capa y `docker-compose.yml` para ejecución en entornos aislados.
- Cobertura de pruebas con **Pytest y Selenium E2E** (24 pruebas pasadas al 100%).

---

## 🏗️ Arquitectura Actual del Proyecto

```
Crypto-Portfolio-Tracker/
├── app/
│   ├── auth/            # Blueprint de Autenticación (Login, Signup, Logout, Idioma)
│   ├── main/            # Blueprint Principal (Dashboard, Candlestick, Portfolio, Alertas)
│   ├── services/        # Servicios Aislados (Bybit/Binance/Coinbase Client, Email Service)
│   ├── static/          # CSS Custom, JS i18n/Chart/Alerts e Ilustraciones Caricatura PNG
│   ├── templates/       # Plantillas Jinja2 Modulares (Bootstrap 5.3)
│   ├── translations/    # Archivos de Internacionalización (es/LC_MESSAGES)
│   ├── extensions.py    # Instanciación Centralizada (SQLAlchemy, LoginManager, Babel)
│   ├── models.py        # Modelos ORM (User, Watchlist, PriceAlerts, AlertLog, Transaction)
│   └── tasks.py         # Evaluador de Alertas en Segundo Plano
├── tests/               # Suite de Pruebas Automáticas (Pytest Unit/Integration + Selenium)
├── documentacion_cambios_proyecto.md # Documentación detallada de cambios de reingeniería
├── .github/workflows/   # Pipeline de Integración Continua (ci.yml)
├── app.py               # Punto de entrada para Producción (Gunicorn / Railway)
├── run.py               # Punto de entrada para Desarrollo Local
├── config.py            # Configuración Centralizada
├── Dockerfile           # Imagen Docker basada en Python 3.11-slim
└── docker-compose.yml   # Orquestación Local
```

---

## 🧪 Suite de Pruebas

```bash
# Ejecutar todas las pruebas unitarias e integración con Pytest
python -m pytest -v --cov=app --cov-report=term-missing
```

---

## 🛠️ Ejecución Local con Docker Compose

```bash
# 1. Clonar el repositorio
git clone https://github.com/nithesh10/Crypto-Portfolio-Tracker.git
cd Crypto-Portfolio-Tracker

# 2. Levantar los servicios con Docker Compose
docker compose up -d --build

# 3. Abrir en el navegador
http://localhost:5000
```

---

## 📄 Licencia y Créditos

- **Proyecto de Examen**: Reingeniería de Software y Contenedorización con Docker.
- **Servidor Nube**: Railway PaaS ([cryptomoney-production.up.railway.app](https://cryptomoney-production.up.railway.app)).
