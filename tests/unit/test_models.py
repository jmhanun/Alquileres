import pytest
from datetime import datetime, timedelta, date
from app import create_app, db
from app.models import Inquilino, Propiedad, Contrato, Factura, Propietario

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

def test_crear_inquilino(app):
    with app.app_context():
        inquilino = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='juan@test.com',
            telefono='1234567890'
        )
        db.session.add(inquilino)
        db.session.commit()
        
        assert inquilino.id is not None
        assert inquilino.nombre == 'Juan Pérez'
        assert inquilino.dni == '12345678'
        assert inquilino.email == 'juan@test.com'
        assert inquilino.telefono == '1234567890'

def test_crear_propiedad(app):
    with app.app_context():
        # Primero crear un propietario
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com',
            telefono='1234567890',
            dni='12345678'
        )
        db.session.add(propietario)
        db.session.commit()

        # Luego crear una propiedad
        propiedad = Propiedad(
            direccion='Calle Falsa 123',
            tipo='Casa',
            ambientes=3,
            propietario=propietario
        )
        db.session.add(propiedad)
        db.session.commit()

        assert propiedad.id is not None
        assert propiedad.direccion == 'Calle Falsa 123'
        assert propiedad.propietario.nombre == 'Ana García'

def test_crear_contrato(app):
    with app.app_context():
        # Crear propietario
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com',
            telefono='1234567890',
            dni='12345678'
        )
        db.session.add(propietario)
        db.session.commit()

        # Crear propiedad
        propiedad = Propiedad(
            direccion='Calle Falsa 123',
            tipo='Casa',
            ambientes=3,
            propietario=propietario
        )
        db.session.add(propiedad)
        db.session.commit()

        # Crear inquilino
        inquilino = Inquilino(
            nombre='Juan Pérez',
            email='juan@test.com',
            telefono='0987654321',
            dni='87654321'
        )
        db.session.add(inquilino)
        db.session.commit()

        # Crear contrato
        contrato = Contrato(
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2025, 12, 31),
            monto_mensual=50000,
            propiedad=propiedad,
            inquilino=inquilino,
            activo=True
        )
        db.session.add(contrato)
        db.session.commit()

        assert contrato.id is not None
        assert contrato.propiedad.direccion == 'Calle Falsa 123'
        assert contrato.inquilino.nombre == 'Juan Pérez'

def test_crear_factura(app):
    with app.app_context():
        # Crear propietario
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com',
            telefono='1234567890',
            dni='12345678'
        )
        db.session.add(propietario)
        db.session.commit()

        # Crear propiedad
        propiedad = Propiedad(
            direccion='Calle Falsa 123',
            tipo='Casa',
            ambientes=3,
            propietario=propietario
        )
        db.session.add(propiedad)
        db.session.commit()

        # Crear inquilino
        inquilino = Inquilino(
            nombre='Juan Pérez',
            email='juan@test.com',
            telefono='0987654321',
            dni='87654321'
        )
        db.session.add(inquilino)
        db.session.commit()

        # Crear contrato
        contrato = Contrato(
            fecha_inicio=date(2024, 1, 1),
            fecha_fin=date(2025, 12, 31),
            monto_mensual=50000,
            propiedad=propiedad,
            inquilino=inquilino,
            activo=True
        )
        db.session.add(contrato)
        db.session.commit()

        # Crear factura
        factura = Factura(
            fecha_emision=date(2024, 2, 1),
            monto=50000,
            contrato=contrato,
            pagado=False
        )
        db.session.add(factura)
        db.session.commit()

        assert factura.id is not None
        assert factura.monto == 50000
        assert factura.contrato.inquilino.nombre == 'Juan Pérez'

def test_dni_unico(app):
    with app.app_context():
        # Crear primer inquilino
        inquilino1 = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='juan@test.com',
            telefono='1234567890'
        )
        db.session.add(inquilino1)
        db.session.commit()
        
        # Intentar crear segundo inquilino con el mismo DNI
        inquilino2 = Inquilino(
            nombre='Pedro Gómez',
            dni='12345678',  # Mismo DNI
            email='pedro@test.com',
            telefono='0987654321'
        )
        db.session.add(inquilino2)
        
        with pytest.raises(Exception):
            db.session.commit()

def test_email_unico(app):
    with app.app_context():
        # Crear primer inquilino
        inquilino1 = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='test@test.com',
            telefono='1234567890'
        )
        db.session.add(inquilino1)
        db.session.commit()
        
        # Intentar crear segundo inquilino con el mismo email
        inquilino2 = Inquilino(
            nombre='Pedro Gómez',
            dni='87654321',
            email='test@test.com',  # Mismo email
            telefono='0987654321'
        )
        db.session.add(inquilino2)
        
        with pytest.raises(Exception):
            db.session.commit()
