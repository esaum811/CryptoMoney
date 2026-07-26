# 🚀 Crypto Portfolio Tracker — Versión Refactorizada

Sistema de rastreo de portafolio de criptomonedas en tiempo real, modernizado mediante reingeniería de software a partir de un proyecto monolítico legacy.

---

## 📖 Descripción

Aplicación web desarrollada con Flask que permite a los usuarios:
- Consultar precios de criptomonedas en tiempo real (API de Bybit)
- Visualizar gráficos de velas (candlestick) interactivos con Plotly.js
- Gestionar una lista de seguimiento (Watchlist) personalizada
- Configurar alertas de precio con notificaciones por email
- Registrar transacciones de compra/venta para calcular ganancias y pérdidas (P&L)
- Cambiar el idioma de la interfaz entre Inglés y Español
- Alternar entre modo oscuro y modo claro

---

## 🏗️ Arquitectura Legada (Original)

El proyecto original presentaba una estructura **monolítica** con todos los archivos en la raíz, sin separación de responsabilidades:

```
Crypto-Portfolio-Tracker/  (ESTRUCTURA ORIGINAL)
├── app.py              ← Inicialización, config, Celery, modelos, filtros, rutas (todo junto)
├── routes.py           ← Rutas mezclando auth + dashboard + API + emails
├── models.py           ← Modelos de datos
├── forms.py            ← Formularios (importa bybit.py al inicio — carga API al importar)
├── database.py         ← Instancia de SQLAlchemy
├── bybit.py            ← Cliente API de Bybit
├── templates/
│   ├── base.html       ← Layout con ~580 líneas (HTML + CSS + JS inline)
│   ├── index.html
│   ├── login.html
│   └── signup.html
├── static/
├── requirements.txt
└── Dockerfile
```

### Problemas identificados:

| Problema | Detalle |
|----------|---------|
| **Importaciones circulares** | `app.py` importa `routes.py`, que importa `app` de `app.py` |
| **Secretos hardcodeados** | `SECRET_KEY = 'Surya123'` y credenciales SMTP en texto plano |
| **Variables globales** | `saved_symbol` y `sent_email = []` — no thread-safe, se pierden al reiniciar |
| **Rutas sin protección** | Endpoints sensibles sin `@login_required` |
| **Código muerto** | Modelo `Crypto`, `CryptoForm`, función `track_prices()` comentada, JS sin uso |
| **Bug de emails** | `send_portfolio_email()` envía emails parciales dentro de un loop |
| **Celery task vacía** | `check_price_alerts()` solo tiene `pass` |
| **Bootstrap 4** | Versión desactualizada, dependiente de jQuery |
| **Sin i18n** | Textos solo en inglés, sin soporte multilenguaje |

---

## ✅ Nueva Arquitectura (Refactorizada)

Se aplicó el patrón **Application Factory** con **Blueprints** de Flask, separando responsabilidades en módulos:

```
Crypto-Portfolio-Tracker/  (NUEVA ESTRUCTURA)
├── app/
│   ├── __init__.py              ← Application Factory (create_app)
│   ├── extensions.py            ← Instancias centralizadas (db, login, babel, migrate)
│   ├── models.py                ← Modelos consolidados + AlertLog + Transaction
│   ├── tasks.py                 ← Tareas de verificación de alertas (corregido)
│   │
│   ├── auth/                    ← Blueprint de Autenticación
│   │   ├── __init__.py
│   │   ├── routes.py            ← Login, Signup, Logout, Cambio de idioma
│   │   └── forms.py             ← SignupForm, LoginForm
│   │
│   ├── main/                    ← Blueprint Principal
│   │   ├── __init__.py
│   │   ├── routes.py            ← Dashboard, Watchlist, Alertas, Portafolio, API
│   │   └── forms.py             ← WatchlistForm, TransactionForm
│   │
│   ├── services/                ← Capa de servicios (lógica de negocio)
│   │   ├── bybit_client.py      ← Cliente API Bybit optimizado
│   │   └── email_service.py     ← Servicio de email centralizado
│   │
│   ├── static/
│   │   ├── css/styles.css       ← Tema oscuro/claro con variables CSS
│   │   └── js/                  ← chart.js, alerts.js, theme.js, language.js
│   │
│   ├── templates/
│   │   ├── base.html            ← Layout Bootstrap 5 responsivo
│   │   ├── auth/                ← Templates de autenticación
│   │   ├── main/                ← Dashboard, Portafolio, Historial de alertas
│   │   ├── components/          ← Toast, Modal de alertas
│   │   └── email/               ← Plantilla de email
│   │
│   └── translations/            ← Archivos i18n (EN/ES)
│       ├── en/LC_MESSAGES/
│       └── es/LC_MESSAGES/
│
├── config.py                    ← Configuración desde variables de entorno
├── run.py                       ← Punto de entrada
├── babel.cfg                    ← Config de extracción de traducciones
├── .env.example                 ← Plantilla de variables de entorno
├── requirements.txt             ← Dependencias actualizadas
├── Dockerfile                   ← Contenedorización
└── README.md                    ← Este archivo
```

### Patrones de diseño aplicados:

- **Application Factory**: La app se crea mediante `create_app()`, permitiendo configuraciones dinámicas y testing.
- **Blueprints**: `auth` y `main` separan responsabilidades de autenticación y funcionalidad principal.
- **Service Layer**: `bybit_client.py` y `email_service.py` encapsulan la lógica de integración externa.
- **Configuración centralizada**: Todas las variables sensibles se cargan desde `.env` vía `config.py`.

---

## 🛠️ Tecnologías

| Categoría | Tecnología |
|-----------|-----------|
| Backend | Python 3.11, Flask 3.0, SQLAlchemy 2.0 |
| Autenticación | Flask-Login |
| Migraciones | Flask-Migrate, Alembic |
| Internacionalización | Flask-Babel 4.0 |
| Frontend | Bootstrap 5.3, Plotly.js 2.27, CSS Variables |
| Tareas en segundo plano | Celery 5.3, Redis |
| Base de datos | SQLite |
| Contenedorización | Docker |
| API externa | Bybit v5 (spot) |

---

## 📦 Instalación

### Requisitos previos
- Python 3.11+
- Redis (para Celery)
- Docker (opcional)

### Instalación local

```bash
# 1. Clonar repositorio
git clone https://github.com/esaum811/CryptoMoney.git
cd CryptoMoney

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env con tus valores

# 5. Compilar traducciones
pybabel compile -d app/translations

# 6. Ejecutar la aplicación
python run.py
```

### Instalación con Docker

```bash
docker build -t crypto-portfolio .
docker run -p 5000:5000 crypto-portfolio
```

---

## 🔐 Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta de Flask | (requerido) |
| `DATABASE_URL` | URI de la base de datos | `sqlite:///crypto.db` |
| `CELERY_BROKER_URL` | URL del broker de Celery | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Backend de resultados Celery | `redis://localhost:6379/0` |
| `MAIL_SENDER` | Email remitente para alertas | (opcional) |
| `MAIL_PASSWORD` | App password del email | (opcional) |
| `FLASK_ENV` | Entorno de ejecución | `development` |

---

## 🌐 Endpoints de la API

| Ruta | Método | Protegida | Descripción |
|------|--------|-----------|-------------|
| `/` | GET, POST | No | Inicio de sesión |
| `/signup` | GET, POST | No | Registro de usuario |
| `/logout` | GET | No | Cerrar sesión |
| `/set_language/<lang>` | GET | No | Cambiar idioma (en/es) |
| `/index` | GET, POST | Sí | Dashboard principal con gráfico |
| `/dashboard` | GET | Sí | Redirige a /index |
| `/candlestick_data` | GET | Sí | Datos OHLC en JSON |
| `/symbol_info` | GET | Sí | Info del ticker en JSON |
| `/add_price_alert` | POST | Sí | Crear alerta de precio |
| `/check_alerts` | GET | Sí | Verificar alertas activas |
| `/add_to_watchlist` | POST | Sí | Agregar a watchlist |
| `/remove_from_watchlist/<name>` | POST | Sí | Eliminar de watchlist |
| `/portfolio` | GET, POST | Sí | Portafolio de transacciones |
| `/alert_history` | GET | Sí | Historial de alertas |
| `/sign_up_for_portfolio_email` | POST | Sí | Preferencia de email |
| `/check_portfolio_email` | GET | Sí | Estado de preferencia |
| `/api/health` | GET | No | Estado del servidor |

---

## ✨ Características Nuevas

| Característica | Descripción |
|---------------|-------------|
| 🌐 **Internacionalización** | Soporte bilingüe Inglés/Español con Flask-Babel |
| 🌙 **Modo Oscuro/Claro** | Toggle de tema con persistencia en localStorage |
| 📊 **Portafolio P&L** | Registro de transacciones con cálculo de ganancias/pérdidas |
| 📋 **Historial de Alertas** | Log de alertas disparadas con fecha, precio y estado |
| 🔔 **Notificaciones Toast** | Reemplaza los `alert()` nativos por toast elegantes |
| 🪟 **Modal de Alertas** | Reemplaza `window.prompt()` por un modal Bootstrap |
| 📈 **Alertas en Gráfico** | Líneas horizontales en el chart indicando límites configurados |
| 🔍 **Búsqueda de Cryptos** | Input con filtro instantáneo para agregar criptomonedas |
| 📱 **Responsive** | Sidebar colapsable en dispositivos móviles |
| 🏥 **Health Check** | Endpoint `/api/health` para monitoreo del servidor |

---

## 🛠️ Correcciones y Ajustes de la Fase 1

Durante las pruebas de integración de la Fase 1 se identificaron y solucionaron los siguientes errores:

1. **Migración de Base de Datos SQLite**:
   - Adición de la columna `is_triggered` a la tabla `price_alerts`.
   - Creación de las tablas `alert_log` (historial) y `transaction` (portafolio P&L).

2. **Corrección en Formulario de Registro (Signup)**:
   - Inclusión del campo `password2` (Repetir Contraseña) y visualización de alertas con mensajes de validación.

3. **Carga y Renderizado del Gráfico Plotly**:
   - Conversión automática de intervalos de tiempo (`15m` → `15`, `1h` → `60`, `1d` → `D`) compatibles con la API v5 de Bybit.
   - Formateo del endpoint `/symbol_info` y mapeo numérico flotante para velas OHLC.
   - Ocultamiento correcto del loader mediante clases nativas `d-none` y `d-flex` de Bootstrap.

4. **Módulo de Portafolio y Registro de Compras/Ventas**:
   - Solución a la falla de Jinja2 por el símbolo `%` en traducciones `gettext`.
   - Soporte para procesamiento directo de solicitudes `POST` al guardar transacciones.

5. **Sincronización de Rutas JavaScript**:
   - Actualización de los endpoints consumidos por `alerts.js` (`/check_portfolio_email`, `/sign_up_for_portfolio_email` y `/remove_from_watchlist/<name>`).

---

## 🚀 Pipeline de Integración Continua (CI/CD - Fase 5)

[![CI Pipeline](https://github.com/nithesh10/Crypto-Portfolio-Tracker/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)

El proyecto cuenta con una canalización automatizada en **GitHub Actions** (`.github/workflows/ci.yml`) que ejecuta 4 trabajos automatizados:
- **Linting & Syntax Check** (`flake8`)
- **Pruebas Unitarias y de Integración con Cobertura (81%)** (`pytest`)
- **Pruebas E2E en Chrome Headless** (`selenium`)
- **Verificación de Construcción Docker** (`docker build`)

Para mayor información sobre la arquitectura de CI, consulte [documentacion_fase_5.md](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/documentacion_fase_5.md).

---

## 👤 Autor

Proyecto de reingeniería de software — Universidad

