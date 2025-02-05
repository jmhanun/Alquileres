import pytest
import json
from datetime import datetime, timedelta
from app import app, db, Inquilino, Propiedad, Contrato, Factura, Propietario

@pytest.fixture(autouse=True)
def clean_db():
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_crear_inquilino(client):
    data = {
        'nombre': 'Juan Perez',  # Sin tilde para evitar problemas de codificación
        'dni': '12345678',
        'email': 'juan@test.com',
        'telefono': '1234567890'
    }
    response = client.post('/api/inquilinos',
                         data=json.dumps(data),
                         content_type='application/json')
    print(f"Response data: {response.data}")  # Agregar logging
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['inquilino']['nombre'] == 'Juan Perez'

def test_crear_propiedad(client):
    # Primero crear un propietario
    propietario_data = {
        'nombre': 'Ana García',
        'email': 'ana@test.com'
    }
    response_propietario = client.post('/api/propietarios',
                                    data=json.dumps(propietario_data),
                                    content_type='application/json')
    assert response_propietario.status_code == 201
    propietario_id = json.loads(response_propietario.data)['id']
    
    # Luego crear la propiedad
    data = {
        'direccion': 'Av. Test 123',
        'tipo': 'Casa',
        'propietario_id': propietario_id
    }
    response = client.post('/api/propiedades',
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert response_data['propiedad']['direccion'] == 'Av. Test 123'

def test_reporte_facturacion_contable(client):
    # Crear datos de prueba
    with app.app_context():
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
        
        factura = Factura(
            contrato_id=contrato.id,
            fecha_emision=datetime.now(),
            monto=50000,
            pagado=True,
            fecha_pago=datetime.now() + timedelta(days=5)
        )
        db.session.add(factura)
        db.session.commit()
    
    # Probar el reporte contable
    response = client.post('/api/reporte-facturacion',
                         data=json.dumps({
                             'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
                             'fecha_fin': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                             'tipo': 'contabilidad'
                         }),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert 'dni' in data[0]
    assert data[0]['dni'] == '12345678'

def test_dni_duplicado(client):
    # Crear primer inquilino
    data1 = {
        'nombre': 'Juan Pérez',
        'dni': '12345678',
        'email': 'juan@test.com',
        'telefono': '1234567890'
    }
    response1 = client.post('/api/inquilinos',
                          data=json.dumps(data1),
                          content_type='application/json')
    assert response1.status_code == 201
    
    # Intentar crear otro inquilino con el mismo DNI
    data2 = {
        'nombre': 'Pedro García',
        'dni': '12345678',  # Mismo DNI
        'email': 'pedro@test.com',
        'telefono': '0987654321'
    }
    response2 = client.post('/api/inquilinos',
                          data=json.dumps(data2),
                          content_type='application/json')
    assert response2.status_code == 400
    assert b'ya existe' in response2.data
