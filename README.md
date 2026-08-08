# 🚀 Crypto Portfolio Tracker

> **Proyecto de Reingeniería de Software**: Transformación de un monolito básico en una plataforma web modular, bilingüe (Español/Inglés), contenedorizada en Docker y desplegada en la nube.

[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://cryptomoney-production.up.railway.app)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-24%2F24%20Passed%20(100%25)-00C853?style=for-the-badge&logo=pytest&logoColor=white)](#-pruebas-automáticas)

---

## 🌐 Enlaces de Producción

* 🔗 **Aplicación Web**: [https://cryptomoney-production.up.railway.app](https://cryptomoney-production.up.railway.app)
* 🔗 **Estado del Servicio (Health Check)**: [https://cryptomoney-production.up.railway.app/api/health](https://cryptomoney-production.up.railway.app/api/health)

---

## 🏛️ Comparativa de Arquitectura: Previa (Legada) vs. Nueva

### 1. Resumen Directo

| Aspecto | 🔴 Arquitectura Previa (Legada) | 🟢 Nueva Arquitectura (Reingeniería) |
| :--- | :--- | :--- |
| **Diseño del Código** | Script único monolítico (`app.py`) con todo acoplado. | **Application Factory Pattern** con arquitectura limpia y modular. |
| **Organización Web** | Rutas, base de datos y vistas mezcladas. | **Blueprints independientes** (`auth` y `main`). |
| **Servicios Externos** | Consultas directas a APIs sin tolerancia a fallos. | **Capa de Servicios Aislada** (`bybit_client.py`, `email_service.py`) con fallback automático (Bybit ➔ Binance ➔ Coinbase). |
| **Idiomas (i18n)** | Texto fijo únicamente en Inglés. | **Soporte Bilingüe Nativo (ES / EN)** con Flask-Babel, traducción en templates y gráficos Plotly.js en español. |
| **Diseño / Temas** | Interfaz rígida sin soporte para temas. | **Diseño Responsivo con Modo Claro y Oscuro**, tarjeta de login en 2 columnas e ilustración personalizada. |
| **Infraestructura** | Ejecución local manual sin aislamiento. | **Contenedorizado en Docker**, Docker Compose y CI/CD en GitHub Actions desplegado en Railway. |

---

### 2. Estructura Visual de Archivos

#### 🔴 Arquitectura Previa (Monolítica)
```text
Crypto-Portfolio-Tracker/
├── app.py            # Rutas, base de datos y lógica en un solo archivo
├── templates/        # Vistas HTML rígidas sin modularidad
└── static/           # Estilos básicos sin traducción
```

#### 🟢 Nueva Arquitectura (Modular y Multi-Capa)
```text
Crypto-Portfolio-Tracker/
├── app/
│   ├── auth/            # Módulo de Autenticación (Login, Registro, Idioma)
│   ├── main/            # Módulo Principal (Dashboard, Gráficos, Portafolio, Alertas)
│   ├── services/        # Clientes API (Bybit/Binance/Coinbase) y Correo
│   ├── static/          # CSS dinámico, JS de traducción e imágenes PNG
│   ├── templates/       # Plantillas Jinja2 modulares (Bootstrap 5.3)
│   ├── translations/    # Catálogos de idioma compilados (es/LC_MESSAGES)
│   ├── extensions.py    # Instanciación centralizada (DB, Auth, Babel)
│   ├── models.py        # Modelos ORM (Usuario, Alertas, Transacciones, Watchlist)
│   └── tasks.py         # Evaluador background de alertas de precio
├── tests/               # Pruebas unitarias e integración (Pytest + Selenium)
├── Dockerfile           # Imagen optimizada en Python 3.11-slim
├── docker-compose.yml   # Orquestación local de contenedores
├── run.py               # Servidor de desarrollo
└── app.py               # Entrada de producción (Gunicorn / Railway)
```

---

## 🙋‍♀️ Guía de Usuario

La guía de usuario detallada en lenguaje simple y humanizado ha sido movida a su propio archivo independiente:
👉 **Consúltala aquí**: [GUIA_USUARIO](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/GUIA_USUARIO)

---

## 🧪 Pruebas Automáticas

Para validar que todo funciona al 100%:

```bash
python -m pytest -v --cov=app --cov-report=term-missing
```

---

## 🛠️ Ejecución Local con Docker

Si deseas probar la aplicación en tu propia computadora utilizando Docker:

```bash
# 1. Clonar el proyecto
git clone https://github.com/nithesh10/Crypto-Portfolio-Tracker.git
cd Crypto-Portfolio-Tracker

# 2. Levantar la aplicación con Docker Compose
docker compose up -d --build

# 3. Entrar desde tu navegador
http://localhost:5000
```

---

## 📜 Créditos y Entrega

Este entregable documenta el proceso de **Reingeniería de Software**, modularización, localización e infraestructura contenedorizada realizada sobre el proyecto *Crypto Portfolio Tracker*.
