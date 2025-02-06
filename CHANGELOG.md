# Changelog
Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.5] - 2025-02-04

### Corregido
- Arreglado el problema de valores indefinidos en los reportes de facturación
- Mejorado el formato de visualización de fechas y estados en los reportes

## [1.2.4] - 2025-02-04

### Cambiado
- Reordenado el menú de navegación para coincidir con el orden de los widgets en la página principal
- Mejorada la consistencia en la navegación del sistema

## [1.2.3] - 2025-02-04

### Agregado
- Íconos en la barra de navegación para Inquilinos e Importar
- Ícono de inicio en el logo del sistema

### Cambiado
- Mejorada la consistencia visual de la barra de navegación
- Actualizado el diseño del logo para incluir ícono

## [1.2.2] - 2025-02-04

### Agregado
- Widget de Contratos en la página principal para acceso directo a la gestión de contratos

### Cambiado
- Mejorado el diseño responsive de los widgets en la página principal

## [1.2.1] - 2025-02-04

### Cambiado
- Simplificada la interfaz de la página principal
- Eliminado el widget de reporte rápido de facturación para mejorar la usabilidad
- Centralizada la funcionalidad de reportes en su sección dedicada

## [1.2.0] - 2025-02-04

### Agregado
- Suite de tests unitarios usando pytest para modelos y rutas
- Configuración de pytest para testing
- Cobertura de código con pytest-cov
- Tests para validación de DNI y email únicos
- Tests para creación de inquilinos, propiedades y reportes
- Fixture para limpiar la base de datos entre tests

### Cambiado
- Mejorado el manejo de errores en la API para DNI y email duplicados
- Optimizada la ruta de reportes de facturación
- Actualizada la validación de fechas en reportes

### Corregido
- Error en la creación de inquilinos con caracteres especiales
- Problema con la comparación de fechas en el reporte de facturación
- Limpieza de la base de datos entre tests para evitar conflictos

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
- Validación de datos en formularios
- Formato de fechas en reportes
- Cálculos de totales en reportes contables

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

## [0.2.0] - 2025-02-06

### Fixed
- Corregido el problema con la inicialización de la base de datos
- Solucionados los errores de migración
- Ajustada la configuración de la base de datos SQLite

### Changed
- Simplificada la configuración de la base de datos en `config.py`
- Mejorada la estructura del proyecto para manejar migraciones

### Added
- Inicialización correcta de la base de datos con todas las tablas necesarias
- Índices optimizados para mejor rendimiento en consultas
- Documentación actualizada para la configuración y ejecución del proyecto

## [0.1.0] - 2025-02-05

### Added
- Implementación inicial del sistema de alquileres
- Modelos básicos: Usuario, Propietario, Inquilino, Propiedad, Contrato, Factura
- Sistema de autenticación
- Configuración inicial del proyecto
