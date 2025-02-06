from .main import main_bp
from .auth import auth_bp
from .propiedades import propiedades_bp
from .inquilinos import inquilinos_bp
from .contratos import contratos_bp
from .facturas import facturas_bp
from .reportes import reportes_bp

__all__ = [
    'main_bp',
    'auth_bp',
    'propiedades_bp',
    'inquilinos_bp',
    'contratos_bp',
    'facturas_bp',
    'reportes_bp'
]
