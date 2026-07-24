# 📕 Documentación Oficial — Fase 3: Pruebas Unitarias y Cobertura (Pytest)

**Proyecto**: Crypto Portfolio Tracker  
**Fase**: 3 — Pruebas Unitarias, Pruebas de Integración y Cobertura de Código con Pytest  
**Ubicación del repositorio**: `ProyectoExamen/Crypto-Portfolio-Tracker`  

---

## 1. Resumen de la Fase 3

En la **Fase 3**, se diseñó e implementó una suite automatizada de **24 pruebas unitarias e integración** utilizando el framework `pytest` y la herramienta de medición de cobertura `pytest-cov`. La suite evalúa todas las capas de la aplicación (modelos ORM, capa de servicios externos con Mocks, controladores de autenticación y endpoints API), alcanzando un **81% de cobertura global** y un **100% de tasa de éxito (24/24 pruebas superadas)**.

---

## 2. Estructura de la Suite de Pruebas (`tests/`)

Se creó el directorio modular `tests/` dentro de `Crypto-Portfolio-Tracker/`:

```text
tests/
├── conftest.py          # Fixtures globales (App Flask en modo TESTING, SQLite en memoria, clientes HTTP)
├── test_models.py       # 5 pruebas unitarias para modelos (User, Watchlist, PriceAlerts, Transaction, AlertLog)
├── test_services.py     # 6 pruebas unitarias para servicios con Mocks (Bybit, Email, Tarea check_price_alerts)
├── test_auth.py         # 7 pruebas de integración para autenticación (Signup, Login, Logout, Idioma, Accesos)
└── test_routes.py       # 6 pruebas para endpoints y API (/api/health, Dashboard, Alertas, Portafolio, Watchlist)
```

---

## 3. Desglose de las 24 Pruebas Implementadas

### 🟢 Capa de Modelos (`test_models.py` - 5 Pruebas)
1. `test_user_password_hashing`: Generación y validación de hash de contraseñas.
2. `test_user_creation_and_uniqueness`: Creación de usuarios e integridad de emails/usernames únicos.
3. `test_portfolio_and_transaction_creation`: Registro y asociación de transacciones P&L al usuario.
4. `test_price_alert_model`: Estado de alertas de precio e historial de eventos disparados.
5. `test_watchlist_model`: Lista de seguimiento de criptomonedas vinculada al usuario.

### 🔵 Capa de Servicios e Integraciones (`test_services.py` - 6 Pruebas)
6. `test_bybit_get_symbols_success`: Mock de la API de Bybit con respuesta exitosa.
7. `test_bybit_get_symbols_error_handling`: Respuesta de fallback ante timeouts o errores de red.
8. `test_bybit_candlestick_data`: Transformación y procesamiento de velados OHLC en DataFrames.
9. `test_email_service_send_alert`: Simulación de envío de correo de alerta de precio alcanzado.
10. `test_email_service_summary`: Generación y envío del resumen diario de portafolio.
11. `test_check_price_alerts_task`: Tarea en segundo plano para verificación de alertas de mercado.

### 🟡 Capa de Autenticación y Seguridad (`test_auth.py` - 7 Pruebas)
12. `test_signup_success`: Registro exitoso de usuario mediante formulario HTTP POST.
13. `test_signup_duplicate_error`: Validación de error al intentar registrar usuario duplicado.
14. `test_login_success`: Inicio de sesión válido y redirección.
15. `test_login_invalid_password`: Rechazo de credenciales incorrectas.
16. `test_logout`: Cierre de sesión y destrucción de la cookie de sesión.
17. `test_unauthorized_access`: Protección de rutas privadas redirigiendo a login.
18. `test_set_language`: Selector de idioma de la sesión (`/set_language/es` y `/set_language/en`).

### 🟠 Capa de Rutas y Endpoints API (`test_routes.py` - 6 Pruebas)
19. `test_health_check_endpoint`: Verificación del endpoint `/api/health` (HTTP 200 y JSON `status: ok`).
20. `test_dashboard_authenticated`: Renderizado correcto de la vista principal con usuario autenticado.
21. `test_add_price_alert_route`: Creación de alertas vía POST JSON (`/add_price_alert`).
22. `test_portfolio_add_transaction`: Registro de transacciones de compra/venta vía POST.
23. `test_toggle_email_preferences`: Actualización de preferencias de recepción de correo.
24. `test_remove_from_watchlist`: Eliminación de pares en la lista de seguimiento.

---

## 4. Resultados de la Ejecución y Cobertura

### Resumen de Ejecución
* **Total de Pruebas**: 24
* **Pasadas**: 24 (100%)
* **Fallidas**: 0

### Matriz de Cobertura (`pytest-cov`)

| Módulo | Cobertura % |
| :--- | :---: |
| `app/models.py` | **100%** |
| `app/auth/forms.py` | **100%** |
| `app/extensions.py` | **100%** |
| `app/services/bybit_client.py` | **90%** |
| `app/auth/routes.py` | **88%** |
| `app/services/email_service.py` | **86%** |
| `app/tasks.py` | **82%** |
| `app/__init__.py` | **82%** |
| `app/main/routes.py` | **66%** |
| **TOTAL PROMEDIO** | **81%** |

---

## 5. Instrucciones de Ejecución

Para ejecutar la suite de pruebas y generar el reporte de cobertura:

```bash
python -m pytest -v --cov=app --cov-report=term-missing
```
