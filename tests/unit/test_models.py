import pytest
from datetime import datetime, timedelta
from app import app, db, Inquilino, Propiedad, Contrato, Factura, Propietario

@pytest.fixture(autouse=True)
def clean_db():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield

@pytest.fixture
def test_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    return app

def test_crear_inquilino(test_app):
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

def test_crear_propiedad(test_app):
    with app.app_context():
        # Primero crear un propietario
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com'
        )
        db.session.add(propietario)
        db.session.commit()
        
        # Luego crear la propiedad asociada al propietario
        propiedad = Propiedad(
            direccion='Av. Test 123',
            tipo='Casa',
            propietario_id=propietario.id
        )
        db.session.add(propiedad)
        db.session.commit()
        
        assert propiedad.id is not None
        assert propiedad.direccion == 'Av. Test 123'
        assert propiedad.tipo == 'Casa'
        assert propiedad.propietario.nombre == 'Ana García'
        assert propiedad.propietario.email == 'ana@test.com'

def test_crear_contrato(test_app):
    with app.app_context():
        # Crear inquilino y propietario
        inquilino = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='juan@test.com',
            telefono='1234567890'
        )
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com'
        )
        db.session.add_all([inquilino, propietario])
        db.session.commit()
        
        # Crear propiedad
        propiedad = Propiedad(
            direccion='Av. Test 123',
            tipo='Casa',
            propietario_id=propietario.id
        )
        db.session.add(propiedad)
        db.session.commit()
        
        # Crear contrato
        fecha_inicio = datetime.now()
        fecha_fin = fecha_inicio + timedelta(days=365)
        contrato = Contrato(
            inquilino_id=inquilino.id,
            propiedad_id=propiedad.id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            monto_mensual=50000
        )
        db.session.add(contrato)
        db.session.commit()
        
        assert contrato.id is not None
        assert contrato.inquilino_id == inquilino.id
        assert contrato.propiedad_id == propiedad.id
        assert contrato.monto_mensual == 50000

def test_crear_factura(test_app):
    with app.app_context():
        # Crear datos necesarios para la factura
        inquilino = Inquilino(
            nombre='Juan Pérez',
            dni='12345678',
            email='juan@test.com',
            telefono='1234567890'
        )
        propietario = Propietario(
            nombre='Ana García',
            email='ana@test.com'
        )
        db.session.add_all([inquilino, propietario])
        db.session.commit()
        
        propiedad = Propiedad(
            direccion='Av. Test 123',
            tipo='Casa',
            propietario_id=propietario.id
        )
        db.session.add(propiedad)
        db.session.commit()
        
        contrato = Contrato(
            inquilino_id=inquilino.id,
            propiedad_id=propiedad.id,
            fecha_inicio=datetime.now(),
            fecha_fin=datetime.now() + timedelta(days=365),
            monto_mensual=50000
        )
        db.session.add(contrato)
        db.session.commit()
        
        # Crear factura
        factura = Factura(
            contrato_id=contrato.id,
            fecha_emision=datetime.now(),
            monto=50000,
            pagado=False
        )
        db.session.add(factura)
        db.session.commit()
        
        assert factura.id is not None
        assert factura.contrato_id == contrato.id
        assert factura.monto == 50000
        assert not factura.pagado

def test_dni_unico(test_app):
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
        
        # Intentar crear otro inquilino con el mismo DNI
        inquilino2 = Inquilino(
            nombre='Pedro García',
            dni='12345678',  # Mismo DNI
            email='pedro@test.com',
            telefono='0987654321'
        )
        db.session.add(inquilino2)
        
        with pytest.raises(Exception):
            db.session.commit()
            
def test_email_unico(test_app):
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
        
        # Intentar crear otro inquilino con el mismo email
        inquilino2 = Inquilino(
            nombre='Pedro García',
            dni='87654321',
            email='juan@test.com',  # Mismo email
            telefono='0987654321'
        )
        db.session.add(inquilino2)
        
        with pytest.raises(Exception):
            db.session.commit()
