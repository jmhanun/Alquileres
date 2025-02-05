# Sistema de Gestión de Alquileres

Sistema web para la gestión de alquileres de propiedades, incluyendo inquilinos, propiedades, contratos y facturación.

## Características

- Gestión de Inquilinos
  - Registro de datos personales incluyendo DNI
  - Historial de contratos
  - Seguimiento de pagos

- Gestión de Propiedades
  - Registro de propiedades con tipo y características
  - Historial de inquilinos
  - Estado de ocupación

- Gestión de Contratos
  - Vinculación inquilino-propiedad
  - Fechas de inicio y fin
  - Monto mensual
  - Estado del contrato

- Facturación
  - Generación automática de facturas mensuales
  - Registro de pagos
  - Estado de cuenta por inquilino

- Reportes
  - Reporte contable anual con movimientos detallados
  - Reporte por inquilino con DNI
  - Reporte por propiedad
  - Exportación a CSV

## Tecnologías Utilizadas

- Backend: Python con Flask
- Base de datos: SQLite con SQLAlchemy
- Frontend: HTML, CSS (Bootstrap), JavaScript
- Reportes: Pandas para exportación CSV

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Iniciar la aplicación:
```bash
python app.py
```

## Estructura del Proyecto

```
sistema-alquileres/
├── app.py              # Aplicación principal y modelos
├── instance/          # Base de datos SQLite
├── static/            # Archivos estáticos (CSS, JS)
├── templates/         # Plantillas HTML
├── venv/              # Entorno virtual
└── requirements.txt   # Dependencias del proyecto
```

## Uso

1. Acceder a la aplicación en `http://localhost:5000`
2. Registrar propiedades e inquilinos
3. Crear contratos vinculando inquilinos con propiedades
4. Generar y gestionar facturas
5. Consultar reportes y exportar a CSV

## Cambios Recientes

### Versión 1.1.0 (Febrero 2025)
- Agregado campo DNI para inquilinos
- Nuevo reporte contable anual
- Exportación de reportes a CSV
- Mejoras en la interfaz de reportes
- Agregada validación de DNI único

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
