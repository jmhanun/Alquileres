from app import create_app, db
from app.models import User, Propietario, Propiedad, Inquilino, Contrato, Factura
from datetime import date, timedelta

def init_db():
    app = create_app('development')
    with app.app_context():
        # Crear tablas
        db.create_all()
        print("Base de datos creada exitosamente")
        
        # Crear usuario administrador si no existe
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123456')
            db.session.add(admin)
            print("Usuario administrador creado")
        
        # Crear propietarios de ejemplo si no existen
        if not Propietario.query.first():
            propietarios = [
                Propietario(
                    nombre='Juan Pérez',
                    email='juan.perez@example.com',
                    telefono='555-0001'
                ),
                Propietario(
                    nombre='María García',
                    email='maria.garcia@example.com',
                    telefono='555-0002'
                )
            ]
            db.session.add_all(propietarios)
            print("Propietarios de ejemplo creados")
            
            # Crear propiedades de ejemplo
            propiedades = [
                Propiedad(
                    direccion='Av. Principal 123',
                    tipo='casa',
                    descripcion='Casa de 3 dormitorios con jardín',
                    propietario=propietarios[0]
                ),
                Propiedad(
                    direccion='Calle Centro 456',
                    tipo='departamento',
                    descripcion='Departamento de 2 dormitorios',
                    propietario=propietarios[0]
                ),
                Propiedad(
                    direccion='Plaza Comercial 789',
                    tipo='local',
                    descripcion='Local comercial en zona céntrica',
                    propietario=propietarios[1]
                )
            ]
            db.session.add_all(propiedades)
            print("Propiedades de ejemplo creadas")
            
            # Crear inquilinos de ejemplo
            inquilinos = [
                Inquilino(
                    nombre='Carlos Rodríguez',
                    dni='30123456',
                    email='carlos.rodriguez@example.com',
                    telefono='555-1001'
                ),
                Inquilino(
                    nombre='Ana Martínez',
                    dni='31234567',
                    email='ana.martinez@example.com',
                    telefono='555-1002'
                )
            ]
            db.session.add_all(inquilinos)
            print("Inquilinos de ejemplo creados")
            
            # Crear contratos de ejemplo
            hoy = date.today()
            contratos = [
                Contrato(
                    fecha_inicio=hoy,
                    fecha_fin=hoy + timedelta(days=365),
                    monto_mensual=50000.0,
                    deposito=50000.0,
                    activo=True,
                    notas='Contrato anual',
                    inquilino=inquilinos[0],
                    propiedad=propiedades[0]
                ),
                Contrato(
                    fecha_inicio=hoy - timedelta(days=180),
                    fecha_fin=hoy + timedelta(days=185),
                    monto_mensual=35000.0,
                    deposito=35000.0,
                    activo=True,
                    notas='Contrato por 1 año',
                    inquilino=inquilinos[1],
                    propiedad=propiedades[1]
                )
            ]
            db.session.add_all(contratos)
            print("Contratos de ejemplo creados")
            
            # Crear facturas de ejemplo
            facturas = [
                Factura(
                    fecha_emision=hoy,
                    monto=50000.0,
                    pagado=False,
                    contrato=contratos[0]
                ),
                Factura(
                    fecha_emision=hoy - timedelta(days=30),
                    monto=35000.0,
                    pagado=True,
                    fecha_pago=hoy - timedelta(days=25),
                    contrato=contratos[1]
                )
            ]
            db.session.add_all(facturas)
            print("Facturas de ejemplo creadas")
        
        # Guardar cambios
        db.session.commit()
        print("Datos iniciales creados exitosamente")

if __name__ == '__main__':
    init_db()
