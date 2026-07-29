# 🚀 Crypto Portfolio Tracker

[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://cryptomoney-production.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-28%2F28%20Passed%20(100%25)-00C853?style=for-the-badge&logo=pytest&logoColor=white)](#-suite-de-pruebas)

> **Plataforma web de monitoreo de criptomonedas en tiempo real, análisis de gráficos candlestick (Plotly), gestión de portafolio P&L, alertas de precio con notificaciones por correo electrónico e internacionalización bilingüe (Español/Inglés).**

---

## 🌐 Despliegue en Producción

El proyecto se encuentra desplegado y activo en la nube a través de **Railway PaaS**:

👉 **URL de la Aplicación**: [https://cryptomoney-production.up.railway.app](https://cryptomoney-production.up.railway.app)  
👉 **Endpoint de Diagnóstico y Salud**: [https://cryptomoney-production.up.railway.app/api/health](https://cryptomoney-production.up.railway.app/api/health)

---

## 📋 Características Principales

- 📈 **Mercado en Tiempo Real & Gráficos Candlestick**: Visualización interactiva de más de 400 pares spot (Plotly.js) con selector de temporalidades (5m, 15m, 1h, 4h, 1d).
- 🛡️ **Cliente API Multi-Fuente Resiliente**: Integración con Bybit API v5 (`/v5/market/instruments-info`) con sistema de **fallbacks automáticos** hacia Binance Global, Binance US y Coinbase API para prevenir bloqueos de IP/WAF.
- 💼 **Gestión de Portafolio P&L**: Registro de operaciones de compra/venta, cálculo consolidado de tenencias, precio promedio de adquisición y porcentaje de Ganancia/Pérdida (P&L).
- 🔔 **Alertas de Precio e Historial**: Configuración de límites superior e inferior de precio con envío de alertas por correo HTML y registro en base de datos (`AlertLog`).
- 🌍 **Soporte Multilingüe (i18n)**: Cambio dinámico de idioma (Español / Inglés) respaldado por `Flask-Babel`, diccionarios en backend y localización en JavaScript.
- 🌗 **Modo Oscuro / Claro**: Tema responsivo (Bootstrap 5.3) adaptable a las preferencias del usuario.
- 🐳 **Contenedorización & CI/CD**: `Dockerfile` multi-capa optimizado con Gunicorn, `docker-compose.yml` para desarrollo y pipeline automatizado en **GitHub Actions**.

---

## 🏗️ Arquitectura e Infraestructura

```
Crypto-Portfolio-Tracker/
├── app/
│   ├── auth/            # Blueprint de Autenticación (Login, Signup, Logout, Idioma)
│   ├── main/            # Blueprint Principal (Dashboard, Candlestick, Portfolio, Alertas)
│   ├── services/        # Servicios Aislados (Bybit/Binance/Coinbase Client, Email Service)
│   ├── static/          # CSS Custom, JavaScript i18n/Chart/Alerts & Assets
│   ├── templates/       # Plantillas Jinja2 Modulares (Bootstrap 5)
│   ├── translations/    # Archivos de Internacionalización (es/LC_MESSAGES)
│   ├── extensions.py    # Instanciación Centralizada (SQLAlchemy, LoginManager, Babel)
│   ├── models.py        # Modelos ORM (User, Watchlist, PriceAlerts, AlertLog, Transaction)
│   └── tasks.py         # Evaluador de Alertas en Segundo Plano
├── tests/               # Suite de 28 Pruebas (Pytest Unit/Integration + Selenium E2E)
├── .github/workflows/   # Pipeline de Integración Continua (ci.yml)
├── app.py               # Punto de entrada para Producción (Gunicorn / Railway)
├── run.py               # Punto de entrada para Desarrollo Local
├── config.py            # Configuración Centralizada y Variables de Entorno
├── Dockerfile           # Imagen Docker Ligera basada en Python 3.11-slim
└── docker-compose.yml   # Orquestación Local con Hot Reload
```

---

## 🧪 Suite de Pruebas

El sistema cuenta con **28 pruebas automatizadas** que garantizan la calidad y confiabilidad del código:

```bash
# Ejecutar todas las pruebas unitarias e integración con Pytest
python -m pytest -v --cov=app --cov-report=term-missing

# Ejecutar pruebas End-to-End (Selenium WebDriver Headless Chrome)
python -m pytest tests/test_selenium_e2e.py -v
```

---

## 🛠️ Ejecución Local con Docker Compose

```bash
# 1. Clonar el repositorio
git clone https://github.com/nithesh10/Crypto-Portfolio-Tracker.git
cd Crypto-Portfolio-Tracker

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar los servicios con Docker Compose
docker compose up -d --build

# 4. Abrir en el navegador
http://localhost:5000
```

---

## 📄 Licencia y Créditos

- **Desarrollado para**: Proyecto de Examen de Reingeniería de Software y Docker.
- **Servidor Nube**: Railway PaaS ([cryptomoney-production.up.railway.app](https://cryptomoney-production.up.railway.app)).
