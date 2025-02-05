# Changelog
Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-02-04

### Agregado
- Campo DNI para inquilinos con validación de unicidad
- Nuevo reporte contable anual con movimientos detallados
- Exportación de reportes a formato CSV
- Selector de año para filtrar el reporte contable
- Visualización del DNI en todos los reportes relacionados con inquilinos

### Cambiado
- Mejorada la interfaz de reportes para soportar diferentes tipos de filtros
- Actualizada la estructura de la base de datos para incluir DNI
- Reorganizada la presentación de datos en reportes para mejor legibilidad

### Corregido
- Validación de campos numéricos en formularios
- Formato de fechas en exportación CSV

## [1.0.0] - 2025-02-01

### Agregado
- Sistema base de gestión de alquileres
- Gestión de propiedades (alta, baja, modificación)
- Gestión de inquilinos (alta, baja, modificación)
- Gestión de contratos
- Sistema de facturación mensual
- Reportes básicos por inquilino y propiedad
- Interfaz web responsive con Bootstrap
- Autenticación de usuarios
- Base de datos SQLite con SQLAlchemy
