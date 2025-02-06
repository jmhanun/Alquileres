from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Propietario(db.Model):
    __tablename__ = 'propietarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    propiedades = db.relationship('Propiedad', backref='propietario', lazy=True,
                                cascade='all, delete-orphan')

class Propiedad(db.Model):
    __tablename__ = 'propiedades'
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    ambientes = db.Column(db.Integer, nullable=True, default=None)
    descripcion = db.Column(db.Text)
    propietario_id = db.Column(db.Integer, db.ForeignKey('propietarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contratos = db.relationship('Contrato', backref='propiedad', lazy='dynamic',
                              cascade='all, delete-orphan')

class Inquilino(db.Model):
    __tablename__ = 'inquilinos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    contratos = db.relationship('Contrato', backref='inquilino', lazy='dynamic',
                              cascade='all, delete-orphan')

class Contrato(db.Model):
    __tablename__ = 'contratos'
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False, index=True)
    fecha_fin = db.Column(db.Date, nullable=False, index=True)
    monto_mensual = db.Column(db.Float, nullable=False)
    deposito = db.Column(db.Float)
    activo = db.Column(db.Boolean, default=True, index=True)
    notas = db.Column(db.Text)
    
    inquilino_id = db.Column(db.Integer, db.ForeignKey('inquilinos.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedades.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    facturas = db.relationship('Factura', backref='contrato', lazy='dynamic',
                             cascade='all, delete-orphan')

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    fecha_emision = db.Column(db.Date, nullable=False, index=True)
    monto = db.Column(db.Float, nullable=False)
    pagado = db.Column(db.Boolean, default=False, index=True)
    fecha_pago = db.Column(db.Date)
    
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Índices compuestos para mejorar el rendimiento de consultas comunes
db.Index('idx_contrato_fechas', Contrato.fecha_inicio, Contrato.fecha_fin)
db.Index('idx_factura_contrato', Factura.contrato_id, Factura.fecha_emision)
