# Sistema de Gestión de Alquileres

Sistema web para la gestión de alquileres de propiedades, incluyendo inquilinos, propiedades, contratos y facturación.

## Características

- Gestión de Inquilinos
  - Registro de datos personales incluyendo DNI
  - Historial de contratos
  - Seguimiento de pagos
  - Validación de DNI y email únicos

- Gestión de Propiedades
  - Registro de propiedades con tipo y características
  - Historial de inquilinos
  - Estado de ocupación
  - Asociación con propietarios

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
  - Filtrado por fechas y tipo de reporte

## Tecnologías Utilizadas

- Backend: Python con Flask
- Base de datos: SQLite con SQLAlchemy
- Frontend: HTML, CSS (Bootstrap), JavaScript
- Reportes: Pandas para exportación CSV
- Testing: pytest, pytest-cov para cobertura de código

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd sistema-alquileres
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Inicializar la base de datos:
```bash
python app.py
```

## Testing

1. Ejecutar los tests:
```bash
python -m pytest
```

2. Ejecutar los tests con reporte de cobertura:
```bash
python -m pytest --cov=app tests/
```

Los tests incluyen:
- Tests unitarios para modelos (Inquilino, Propiedad, Contrato, Factura)
- Tests de integración para rutas de la API
- Validación de restricciones únicas (DNI, email)
- Tests de reportes y facturación

## Uso

1. Iniciar el servidor:
```bash
python app.py
```

2. Abrir en el navegador:
```
http://localhost:5000
```

## Estructura del Proyecto

```
sistema-alquileres/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── templates/         # Plantillas HTML
├── static/           # Archivos estáticos
└── tests/           # Suite de tests
    ├── unit/       # Tests unitarios
    └── integration/ # Tests de integración
```

## Contribución

1. Fork el proyecto
2. Crear una rama para su feature (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Versionado

Usamos [SemVer](http://semver.org/) para el versionado. Para ver las versiones disponibles, vea las [etiquetas en este repositorio](https://github.com/your/project/tags).

## Autores

* **Juan Manuel Hanun** - *Trabajo inicial*

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE.md](LICENSE.md) para más detalles.
