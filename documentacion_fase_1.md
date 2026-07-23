# 📘 Documentación Oficial — Fase 1: Ingeniería Reversa y Refactorización (Código Limpio)

**Proyecto**: Crypto Portfolio Tracker  
**Fase**: 1 — Ingeniería Reversa, Refactorización, Arquitectura Modular y Código Limpio  
**Ubicación del repositorio**: `ProyectoExamen/Crypto-Portfolio-Tracker`  

---

## 1. Resumen de la Fase 1

En la **Fase 1**, se realizó un análisis exhaustivo de ingeniería reversa sobre el proyecto monolítico heredado ([nithesh10/Crypto-Portfolio-Tracker](https://github.com/nithesh10/Crypto-Portfolio-Tracker)). Se reestructuró por completo la base de código aplicando patrones de diseño modernos, arquitectura modular basada en **Flask Blueprints**, patrón **Application Factory**, centralización de configuración y eliminación de deuda técnica.

---

## 2. Arquitectura Previa (Monolítica Legada) vs. Nueva Arquitectura

### 2.1 Estructura Monolítica Legada
La estructura original tenía todos los módulos fuertemente acoplados en la raíz sin separación de responsabilidades:

```
Crypto-Portfolio-Tracker/ (LEGACY)
├── app.py              # Mezclaba configuración, inicialización, Celery, modelos, filtros y rutas
├── routes.py           # Mezclaba rutas de autenticación, dashboard, API y envío de emails
├── models.py           # Modelos de base de datos desactualizados
├── forms.py            # Formularios WTForms (ejecutaba peticiones HTTP a la API al importar)
├── database.py         # Instancia global aislada de SQLAlchemy
├── bybit.py            # Cliente de API de Bybit desorganizado
└── templates/
    └── base.html       # Layout de ~580 líneas mezclando HTML, Vanilla CSS y scripts inline
```

### 2.2 Nueva Arquitectura Modular Propuesta
Se reestructuró el proyecto aplicando el patrón **Application Factory** y **Blueprints**:

```
Crypto-Portfolio-Tracker/ (MODERNA / REFACTORIZADA)
├── config.py                       # Configuración centralizada basada en variables de entorno (.env)
├── run.py                          # Punto de entrada principal de la aplicación
├── requirements.txt                # Dependencias actualizadas
├── Dockerfile                      # Archivo de contenedorización
├── app/
│   ├── __init__.py                 # Fábrica de aplicaciones create_app() y filtros Jinja2
│   ├── extensions.py               # Instanciación de SQLAlchemy, LoginManager, Migrate y Babel
│   ├── models.py                   # Modelos ORM unificados (User, Watchlist, PriceAlerts, AlertLog, Transaction)
│   ├── tasks.py                    # Procesamiento asíncrono de alertas de precio
│   ├── auth/                       # Blueprint de Autenticación
│   │   ├── __init__.py
│   │   ├── forms.py                # Formularios de Login y Registro con validación Regex
│   │   └── routes.py               # Controladores de inicio de sesión, registro y cierre de sesión
│   ├── main/                       # Blueprint Principal
│   │   ├── __init__.py
│   │   ├── forms.py                # Formularios de Watchlist y Transacciones P&L
│   │   └── routes.py               # Controladores de gráfico candlestick, alertas, watchlist y portafolio
│   └── services/                   # Capa de Servicios Externos
│       ├── __init__.py
│       ├── bybit_client.py         # Cliente optimizado para la API v5 de Bybit (Tickers, OHLC, Kline)
│       └── email_service.py        # Servicio unificado de correo SMTP (HTML templates)
```

---

## 3. Problemas Identificados y Soluciones Aplicadas

| # | Problema Detectado en Código Legado | Impacto en el Sistema | Solución Aplicada en Fase 1 |
|---|-------------------------------------|-----------------------|-----------------------------|
| **1** | **Importaciones Circulares** | `app.py` importaba `routes.py` y `routes.py` importaba `app` de `app.py`, causando fallos de inicialización. | Implementación del patrón **Application Factory** (`create_app()`) con registro diferido de Blueprints (`auth_bp`, `main_bp`). |
| **2** | **Secretos Hardcodeados** | Claves de sesión (`SECRET_KEY = 'Surya123'`) y contraseñas SMTP visibles en texto plano. | Centralización en `config.py` con lectura dinámica de variables de entorno mediante `python-dotenv`. |
| **3** | **Variables Globales Mutables** | Se usaban variables globales (`saved_symbol` y `sent_email = []`) no thread-safe que se perdían al reiniciar la app. | Reemplazo por sesiones HTTP seguras de Flask (`session['saved_symbol']`) y persistencia en base de datos (`AlertLog`). |
| **4** | **Rutas Sensibles Sin Protección** | Endpoints críticos (como `/portfolio`, `/add_price_alert`) no verificaban la autenticación del usuario. | Adición del decorador `@login_required` de Flask-Login en todas las rutas privadas. |
| **5** | **Bug en Envío de Correos Diarios** | `send_portfolio_email()` enviaba múltiples correos incompletos dentro de un ciclo `for`. | Refactorización en `send_portfolio_summary()` para compilar todo el portafolio en **un único correo consolidated**. |
| **6** | **Tarea Celery Incompleta** | La función periódica `check_price_alerts()` en el código legacy solo contenía la sentencia `pass`. | Implementación completa de la lógica de comparación de precios en tiempo real vs. límites en `app/tasks.py`. |
| **7** | **Límites de Alertas Inactivos** | El modelo `Watchlist` tenía campos `lower_limit` y `upper_limit` que no se utilizaban en la interfaz. | Creación del modelo y tabla `PriceAlerts` con control del estado `is_triggered` e integración visual con Plotly.js. |
| **8** | **Código Muerto y Remanentes** | Clases e importaciones sin uso (`Crypto`, `CryptoForm`, scripts JS abandonados). | Limpieza total de código muerto y depreciado para mantener la base de código limpia (Clean Code). |
| **9** | **Falta de Internacionalización** | La interfaz solo soportaba inglés estático. | Integración de **Flask-Babel** para soporte bilingüe (Español / Inglés) con cambio de idioma al vuelo. |
| **10** | **Interfaz Desactualizada (Bootstrap 4)** | Estilos desactualizados y dependientes de jQuery. | Actualización a **Bootstrap 5**, plantilla bilingüe con soporte para **Modo Oscuro / Claro** y notificaciones Toast. |

---

## 4. Entregables Cumplidos de la Fase 1

- [x] Repositorio estructurado bajo arquitectura modular de Blueprints.
- [x] Archivo `config.py` centralizado.
- [x] Modelos de base de datos SQLAlchemy segregados en `app/models.py`.
- [x] Documentación técnica de arquitectura previa y actual en [README.md](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/README.md).
