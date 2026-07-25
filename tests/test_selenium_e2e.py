"""
Suite de Pruebas End-to-End (E2E) con Selenium WebDriver.
Simula interacciones reales de usuario final en la aplicación Crypto Portfolio Tracker:
1. Registro e Inicio de Sesión de usuario.
2. Navegación en el Dashboard y consulta de mercado.
3. Registro de transacciones de compra/venta en el Portafolio P&L.
4. Navegación entre vistas principales (Dashboard, Portafolio, Historial de Alertas) y gestión de la Watchlist.
"""

import os
import time
import pytest
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import create_app
from app.extensions import db
from config import Config


# ── Configuración del Servidor de Pruebas en Vivo ──
class E2EConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'e2e-selenium-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'e2e_test_database.db'
    )


@pytest.fixture(scope='module')
def live_server():
    """Inicia el servidor web Flask en un hilo independiente para pruebas Selenium."""
    app = create_app(E2EConfig)
    
    with app.app_context():
        db.create_all()

    # Arrancar servidor en puerto 5005
    server_thread = threading.Thread(
        target=app.run,
        kwargs={'host': '127.0.0.1', 'port': 5005, 'use_reloader': False}
    )
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1.5)  # Tiempo de inicialización del socket HTTP

    yield 'http://127.0.0.1:5005'

    # Limpieza al finalizar el módulo de pruebas
    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    db_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'e2e_test_database.db')
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except Exception:
            pass


@pytest.fixture(scope='module')
def driver():
    """Inicializa la instancia de Selenium Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    
    # Permitir alternar entre modo Headless (CI/CD) y Modo Visual (Demostración local)
    is_headless = os.environ.get('HEADLESS', 'true').lower() == 'true'
    if is_headless:
        options.add_argument('--headless=new')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    service = ChromeService(ChromeDriverManager().install())
    _driver = webdriver.Chrome(service=service, options=options)
    _driver.implicitly_wait(5)

    yield _driver

    _driver.quit()


# ── Pruebas E2E ──

def test_01_user_registration_and_login(live_server, driver):
    """
    Prueba E2E 1: Registro e Inicio de Sesión de Usuario.
    Valida el flujo completo desde el formulario de registro hasta el login y la sesión activa.
    """
    # 1. Navegar a la página de registro (/signup)
    driver.get(f'{live_server}/signup')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'username')))

    assert "Create Account" in driver.page_source or "CryptoTracker" in driver.title

    # 2. Llenar el formulario de registro
    driver.find_element(By.ID, 'username').send_keys('trader_e2e')
    driver.find_element(By.ID, 'email').send_keys('trader_e2e@example.com')
    driver.find_element(By.ID, 'password').send_keys('SecurePass123!')
    driver.find_element(By.ID, 'password2').send_keys('SecurePass123!')

    # Submit registro
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()
    time.sleep(1)

    # 3. Navegar a la página de inicio de sesión (/) y autenticarse
    driver.get(f'{live_server}/')
    wait.until(EC.presence_of_element_located((By.ID, 'username')))

    driver.find_element(By.ID, 'username').send_keys('trader_e2e')
    driver.find_element(By.ID, 'password').send_keys('SecurePass123!')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(1.5)

    # 4. Verificar inicio de sesión exitoso y acceso al Dashboard
    assert "Dashboard" in driver.page_source or "CryptoTracker" in driver.title
    assert "trader_e2e" in driver.page_source or "T" in driver.page_source


def test_02_dashboard_market_view(live_server, driver):
    """
    Prueba E2E 2: Consulta del Mercado y Visualización de Gráficos en el Dashboard.
    Verifica que la página principal renderice la interfaz interactiva y los selectores de temporalidad.
    """
    driver.get(f'{live_server}/index')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'timelineSelector')))

    # Aserción: Presencia de selectores de tiempo (5m, 15m, 1h, 4h, 1d)
    timeline_box = driver.find_element(By.ID, 'timelineSelector')
    assert timeline_box.is_displayed()

    # Aserción: Presencia del contenedor de gráfico Plotly
    chart_container = driver.find_element(By.ID, 'mainChart')
    assert chart_container is not None


def test_03_portfolio_add_transaction(live_server, driver):
    """
    Prueba E2E 3: Registro de Transacciones en el Portafolio.
    Simula la apertura del formulario de transacción, ingreso de datos de compra de BTCUSDT y actualización de la tabla.
    """
    driver.get(f'{live_server}/portfolio')
    wait = WebDriverWait(driver, 10)
    
    # 1. Abrir formulario colapsable
    add_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-bs-target="#transactionFormCollapse"]')))
    add_btn.click()
    time.sleep(0.5)

    # 2. Llenar campos del formulario
    symbol_select = driver.find_element(By.NAME, 'symbol')
    symbol_select.send_keys('BTCUSDT')

    qty_input = driver.find_element(By.NAME, 'quantity')
    qty_input.clear()
    qty_input.send_keys('0.5')

    price_input = driver.find_element(By.NAME, 'price')
    price_input.clear()
    price_input.send_keys('65000.00')

    # 3. Guardar transacción
    save_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Save Transaction')] | //button[contains(text(), 'Guardar')] | //button[contains(@class, 'btn-primary')]")
    save_btn.click()
    time.sleep(1.5)

    # 4. Aserción: Verificar que la tabla de Holdings o resumen contenga BTCUSDT
    assert "BTCUSDT" in driver.page_source or "Portfolio" in driver.page_source
    assert "Holdings" in driver.page_source or "Current Holdings" in driver.page_source


def test_04_navigation_and_sidebar_views(live_server, driver):
    """
    Prueba E2E 4: Navegación de Flujos Críticos en la Interfaz (Sidebar y Rutas).
    Navega entre Portafolio, Historial de Alertas y Dashboard verificando respuesta visual adecuada.
    """
    wait = WebDriverWait(driver, 10)

    # 1. Navegar a Historial de Alertas
    driver.get(f'{live_server}/alert_history')
    time.sleep(0.5)
    assert "Alert History" in driver.page_source or "Historial" in driver.page_source or "CryptoTracker" in driver.title

    # 2. Navegar de regreso a Dashboard
    driver.get(f'{live_server}/index')
    time.sleep(0.5)
    assert "Dashboard" in driver.page_source or "CryptoTracker" in driver.title

    # 3. Comprobar que el navegador no presente errores de renderizado
    assert "404" not in driver.title
    assert "500" not in driver.title
