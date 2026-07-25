# Documentación Fase 4: Pruebas de Interacción Real (Selenium E2E)

## 📌 Resumen Ejecutivo
En la **Fase 4** se implementó una suite automatizada de **Pruebas End-to-End (E2E)** utilizando **Selenium WebDriver** y **Pytest** para validar los flujos de usuario críticos (*Critical User Journeys - CUJs*) del sistema **Crypto Portfolio Tracker**.

---

## 💡 Ámbito Empresarial vs. Rúbrica del Proyecto

### ¿Cuántas pruebas E2E deben realizarse en la industria?
En el entorno empresarial real, el equipo de desarrollo y QA automatizado se rige por la **Pirámide de Automatización de Pruebas (Test Pyramid de Mike Cohn)**:

1. **Pruebas Unitarias (Base - 60-70%):** Pruebas aisladas, rápidas y estables para funciones y modelos.
2. **Pruebas de Integración / API (Centro - 20-30%):** Validación de endpoints HTTP, servicios y base de datos sin renderizar UI.
3. **Pruebas E2E / UI (Cúspide - 5-10%):** Simulación de usuario real en navegador.

#### Justificación del número de pruebas:
- **Costo y Rendimiento:** Las pruebas E2E requieren levantar navegadores reales (Chrome), consumiendo recursos significativos y tardando segundos por cada flujo.
- **Flakiness (Inestabilidad):** Sensibles a latencia de red, renderizado de DOM y animaciones.
- **Conclusión Profesional:** En la industria **no se automatiza toda la UI**, sino únicamente los **3 a 5 flujos críticos de negocio ("Happy Paths")**.

Para este proyecto se construyeron **4 pruebas E2E exhaustivas** que cubren el 100% de la funcionalidad clave exigida por la rúbrica.

---

## 🧪 Detalle de la Suite de Pruebas E2E (`test_selenium_e2e.py`)

| ID | Nombre de la Prueba | Descripcion y Flujo Evaluado | Aserciones Clave de Selenium |
| :--- | :--- | :--- | :--- |
| **E2E-01** | `test_01_user_registration_and_login` | **Flujo de Autenticación:** Registro de usuario (`/auth/signup`), redirección y login exitoso (`/auth/login`). | Verificación de elementos en DOM (`#username`), cambio de URL y sesión activa visible. |
| **E2E-02** | `test_02_dashboard_market_view` | **Consulta de Mercado:** Carga del Dashboard (`/index`), presencia del gráfico interactivo y selectores de tiempo. | Visibilidad de `#timelineSelector` y del contenedor Plotly `#mainChart`. |
| **E2E-03** | `test_03_portfolio_add_transaction` | **Operaciones de Portafolio:** Apertura de formulario, registro de compra de `BTCUSDT` y renderizado en tabla. | Presencia del registro en la tabla de Holdings y actualización del estado del portafolio. |
| **E2E-04** | `test_04_navigation_and_sidebar_views` | **Navegación Integral:** Transición fluida entre Dashboard, Portafolio e Historial de Alertas sin errores. | Verificación de títulos, código HTTP 200 implícito en DOM y ausencia de pantallas de error (404/500). |

---

## ⚙️ Arquitectura Técnica de Pruebas

- **Live Server Dynamic Fixture:** Se configuró un fixture en Pytest que levanta un servidor Flask en un hilo independiente (`threading.Thread`) escuchando en `http://127.0.0.1:5005`, aislando la base de datos a `sqlite:///e2e_test_database.db`.
- **Automatic Driver Management:** Uso de `webdriver-manager` para la descarga e instanciación automática del Chrome Driver adecuado.
- **Soporte Headless / Headed:**
  - **Modo Headless (`HEADLESS=true`):** Ejecución rápida y silenciosa optimizada para **GitHub Actions (Fase 5)**.
  - **Modo Visual (`HEADLESS=false`):** Permite ver la ventana de Chrome interactuando en tiempo real para demostraciones en vivo.

---

## 🚀 Guía de Ejecución

### 1. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecución en Modo Silencioso (Headless)
```bash
python -m pytest tests/test_selenium_e2e.py -v
```

### 3. Ejecución en Modo Visual (Demostración interactiva)
```powershell
$env:HEADLESS="false"; python -m pytest tests/test_selenium_e2e.py -v
```

---

## ✅ Resultado de Ejecución y Cobertura

Todas las 4 pruebas de interacción real E2E fueron ejecutadas y aprobadas al 100% en verde:
- `test_01_user_registration_and_login`: **PASSED**
- `test_02_dashboard_market_view`: **PASSED**
- `test_03_portfolio_add_transaction`: **PASSED**
- `test_04_navigation_and_sidebar_views`: **PASSED**
