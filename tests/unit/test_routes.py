import pytest
import json
from datetime import datetime, timedelta
from flask import url_for
from app import create_app, db
from app.models import User, Inquilino, Propiedad, Contrato, Factura, Propietario
from datetime import date

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

@pytest.fixture
def auth_client(app, client):
    with app.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('test123456')
        db.session.add(user)
        db.session.commit()
    
    client.post('/auth/login', data={
        'username': 'test',
        'password': 'test123456'
    }, follow_redirects=True)
    return client

def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_login(client):
    with client.application.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('test123456')
        db.session.add(user)
        db.session.commit()
    
    response = client.post('/auth/login', data={
        'username': 'test',
        'password': 'test123456'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_propiedades_lista(auth_client, app):
    with app.app_context():
        # Crear un propietario
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com',
            telefono='1234567890',
            dni='12345678'
        )
        db.session.add(propietario)
        db.session.commit()

        # Crear una propiedad
        propiedad = Propiedad(
            direccion='Calle Falsa 123',
            tipo='Casa',
            ambientes=3,
            propietario=propietario
        )
        db.session.add(propiedad)
        db.session.commit()

        response = auth_client.get('/propiedades/lista')
        assert response.status_code == 200
        assert b'Calle Falsa 123' in response.data

def test_inquilinos_lista(auth_client, app):
    with app.app_context():
        inquilino = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='juan@test.com',
            telefono='1234567890'
        )
        db.session.add(inquilino)
        db.session.commit()
    
    response = auth_client.get('/inquilinos/lista')
    assert response.status_code == 200
    assert b'Juan P' in response.data

def test_contratos_lista(auth_client, app):
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

        response = auth_client.get('/contratos/lista')
        assert response.status_code == 200
        assert b'Calle Falsa 123' in response.data
        assert b'Juan P' in response.data

def test_facturas_lista(auth_client, app):
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

        response = auth_client.get('/facturas/lista')
        assert response.status_code == 200
        assert b'50000' in response.data

def test_reportes_dashboard(auth_client, app):
    with app.app_context():
        # Crear datos necesarios
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

        response = auth_client.get('/reportes/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
