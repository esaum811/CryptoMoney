# 📄 Documentación Completa de Cambios - Reingeniería de Software

## 📌 Resumen del Proyecto

Este documento detalla todas las modificaciones, mejoras y refactorizaciones realizadas en el proyecto **Crypto Portfolio Tracker** como parte de un proceso integral de **Reingeniería de Software**.

---

## 🛠️ Detalle de Cambios Realizados

### 1. Sistema de Internacionalización y Traducción al Español (i18n)
- **Corrección de Cobertura de Idioma**: Se rectificó y completó la traducción de inglés a español en toda la aplicación.
- **Diccionario de Traducción Jinja2 (`app/__init__.py`)**: Se expandió el diccionario `SPANISH_TRANSLATIONS` cubriendo cadenas de autenticación, encabezados de tablas, notificaciones toast, modalidades de alerta y correos electrónicos.
- **Localización de Gráficos Plotly.js (`app/static/js/chart.js`)**: Se registró el catálogo de idioma en español de Plotly (`Plotly.register`) traduciendo los tooltips de la barra de herramientas (*Lasso Select* ➔ *Selección de lazo*, *Box Select* ➔ *Selección en caja*, *Zoom*, *Pan* ➔ *Desplazar*, *Reset axes* ➔ *Restablecer ejes*, *Download plot as a png* ➔ *Descargar gráfico como PNG*).
- **Compilación de Catálogos PyBabel**: Se actualizaron y recompilaron los archivos binarios de catálogo `.po` ➔ `.mo` en `app/translations/es/LC_MESSAGES/`.
- **Persistencia de Cookie de Idioma (`app/auth/routes.py`)**: Se añadió el envío de la cookie HTTP `lang` al cambiar de idioma para reflejar los cambios instantáneamente en JavaScript.

### 2. Rediseño Completo de la Pantalla de Inicio de Sesión (`login.html`)
- **Estructura en 2 Columnas**: Layout limpio con la sección de marca e ilustración a la izquierda y el formulario de acceso a la derecha.
- **Ilustración Personalizada Estilo Caricatura**: Creación e integración del activo visual [crypto_cartoon_swap.png](file:///c:/Users/esaum/OneDrive/Documentos/Mi-Primer-Docker/ProyectoExamen/Crypto-Portfolio-Tracker/app/static/crypto_cartoon_swap.png) (intercambio 2D de Bitcoin y Ethereum) con transparencia alfa (sin marco ni fondo cuadrado).
- **Eliminación del Marco en la Imagen**: La columna izquierda no tiene bordes ni contenedor rígido (`background: transparent`), dejando flotar la ilustración y los títulos sobre el lienzo general.
- **Jerarquía de Textos**: Títulos de marca situados **por encima** de la ilustración.

### 3. Rediseño y Ajuste de la Pantalla de Registro (`signup.html`)
- **Corrección de Desbordamiento Vertical**: Se eliminó el margen negativo (`margin-top: -80px`) que hacía que la tarjeta sobresaliera por el borde superior de la pantalla.
- **Dimensiones Compactas**: Reducción del ancho a `480px` con paddings optimizados y menor espaciado entre campos de entrada.

### 4. Soporte Completo Dual: Modo Claro y Modo Oscuro (Light/Dark Mode)
- **Modo Claro (`data-bs-theme="light"`)**:
  - Las tarjetas de login y signup cambian dinámicamente a **color blanco puro (`#ffffff`)** con sombras suaves y bordes gris claro.
  - Los títulos, subtítulos y textos de marca cambian a tonos oscuros de alto contraste (`#1e2022` y `#6c757d`) para garantizar visibilidad total.
  - Los campos de texto (*inputs*) pasan a fondo claro (`#f8fafc`) con bordes limpios en azul.
- **Modo Oscuro (`data-bs-theme="dark"`)**:
  - Mantiene la estética de vidrio translúcido oscuro con bordes e indicadores en azul neón resplandeciente.

### 5. Corrección de Estructura de Pantalla (`base.html`)
- **Ocultamiento de Barra Lateral en Páginas No Autenticadas**: Se envolvió el elemento `<aside class="sidebar">` dentro de `{% if current_user and current_user.is_authenticated %}`. Con esto se eliminó la línea vertical divisoria en las pantallas de Login y Signup, manteniéndola activa únicamente en el Dashboard principal.

---

## 🧪 Pruebas de Calidad (Testing)

Se ejecutó la suite de pruebas unitarias e integración comprobando un **100% de éxito**:
- Pruebas pasadas: **24 de 24**.
