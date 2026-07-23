"""Punto de entrada principal para la ejecución de la aplicación Flask."""

from app import create_app

# Crear la instancia de la aplicación mediante el patrón Application Factory
app = create_app()

if __name__ == '__main__':
    # Ejecutar en modo depuración para desarrollo local
    app.run(debug=True)

