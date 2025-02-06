from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
from config import config

# Inicializar las extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicie sesión para acceder a esta página.'

@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuración básica
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config['SECRET_KEY'] = 'dev'
    
    # Asegurarse de que el directorio instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configurar la base de datos con ruta absoluta
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Añadir variables globales a los templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Crear las tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Configurar el sistema de logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/alquileres.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Inicialización del sistema de alquileres')
    
    # Registrar blueprints
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.propietarios import propietarios_bp
    from app.views.inquilinos import inquilinos_bp
    from app.views.propiedades import propiedades_bp
    from app.views.contratos import contratos_bp
    from app.views.facturas import facturas_bp
    from app.views.reportes import reportes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(propietarios_bp, url_prefix='/propietarios')
    app.register_blueprint(inquilinos_bp, url_prefix='/inquilinos')
    app.register_blueprint(propiedades_bp, url_prefix='/propiedades')
    app.register_blueprint(contratos_bp, url_prefix='/contratos')
    app.register_blueprint(facturas_bp, url_prefix='/facturas')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    
    return app
