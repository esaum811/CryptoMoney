"""Punto de entrada principal para la aplicación Flask en producción (compatible con Railway, Gunicorn y Docker)."""
import os
from app import create_app

# Crear la instancia de la aplicación mediante el patrón Application Factory
app = create_app()

if __name__ == '__main__':
    # Leer el puerto proporcionado dinámicamente por la variable de entorno PORT (predeterminado: 5000)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
