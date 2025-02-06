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
- `propietarios`: Propietarios de inmuebles
- `inquilinos`: Inquilinos de las propiedades
- `propiedades`: Propiedades disponibles
- `contratos`: Contratos de alquiler
- `facturas`: Facturas y pagos

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
