# Sistema de Gestión de Alquileres

Sistema web para la gestión de alquileres, propiedades, inquilinos y propietarios.

## Requisitos

- Python 3.9+
- pip
- virtualenv

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tuusuario/sistema-alquileres.git
cd sistema-alquileres
```

2. Crear y activar el entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar las variables de entorno:
```bash
cp .env.example .env
```
Edita el archivo `.env` con tus configuraciones.

## Configuración de la Base de Datos

La base de datos se inicializa automáticamente en el directorio raíz del proyecto. Para configurar la base de datos:

1. Inicializar la base de datos:
```bash
flask db upgrade
```

## Autenticación

El sistema utiliza autenticación y autorización para proteger el acceso a las funcionalidades. Los usuarios pueden registrarse y iniciar sesión para acceder a la aplicación.

## Ejecución

1. Activar el entorno virtual (si no está activado):
```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Establecer la variable de entorno FLASK_APP:
```bash
export FLASK_APP=run.py  # En Windows: set FLASK_APP=run.py
```

3. (Opcional) Activar el modo desarrollo:
```bash
export FLASK_ENV=development  # En Windows: set FLASK_ENV=development
```

4. Ejecutar el servidor:
```bash
flask run
```

La aplicación estará disponible en `http://127.0.0.1:5000/`

## Estructura del Proyecto

```
sistema-alquileres/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   └── static/
├── migrations/
├── instance/
├── tests/
├── config.py
├── requirements.txt
└── run.py
```

## Base de Datos

El sistema utiliza SQLite como base de datos por defecto. Las tablas principales son:

- `user`: Usuarios del sistema
- `propietarios`: Propietarios de inmuebles (nombre, dni, email, teléfono)
- `inquilinos`: Inquilinos de las propiedades (nombre, dni, email, teléfono)
- `propiedades`: Propiedades disponibles (dirección, tipo, ambientes, descripción)
- `contratos`: Contratos de alquiler (fechas, monto mensual, depósito)
- `facturas`: Facturas y pagos (fecha emisión, monto, estado de pago)

## Mejoras Planificadas

Para ver la lista completa de mejoras planificadas y características pendientes, consulte el archivo [TODO.md](TODO.md).

## Versiones de Dependencias Principales

- Flask==2.3.3
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- Flask-WTF==1.2.1
- Werkzeug==2.3.7
- SQLAlchemy==2.0.23

## Desarrollo

Para contribuir al proyecto:

1. Crear una nueva rama para tu feature:
```bash
git checkout -b feature/nueva-funcionalidad
```

2. Realizar cambios y commits
3. Crear un pull request

### Migraciones de Base de Datos

Para crear una nueva migración:
```bash
flask db migrate -m "descripción de los cambios"
```

Para aplicar las migraciones:
```bash
flask db upgrade
```

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para el historial de cambios.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
