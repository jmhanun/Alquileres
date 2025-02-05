from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, case
import pandas as pd
import os
from werkzeug.utils import secure_filename

# Configuración para la carga de archivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alquileres.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# Modelos
class Propietario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    propiedades_list = db.relationship('Propiedad', backref='propietario', lazy=True)

class Propiedad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    propietario_id = db.Column(db.Integer, db.ForeignKey('propietario.id'), nullable=False)
    contratos_list = db.relationship('Contrato', backref='propiedad', lazy=True)

class Inquilino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    contratos_list = db.relationship('Contrato', backref='inquilino', lazy=True)

class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    monto_mensual = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    inquilino_id = db.Column(db.Integer, db.ForeignKey('inquilino.id'), nullable=False)
    propiedad_id = db.Column(db.Integer, db.ForeignKey('propiedad.id'), nullable=False)
    facturas_list = db.relationship('Factura', backref='contrato', lazy=True)

class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_emision = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Float, nullable=False)
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.Date)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/facturas')
def facturas():
    facturas = Factura.query.all()
    contratos = Contrato.query.all()
    return render_template('facturas.html', facturas=facturas, contratos=contratos)

@app.route('/propiedades')
def propiedades():
    propiedades = Propiedad.query.all()
    return render_template('propiedades.html', propiedades=propiedades)

@app.route('/inquilinos')
def inquilinos():
    inquilinos = Inquilino.query.all()
    return render_template('inquilinos.html', inquilinos=inquilinos)

@app.route('/contratos')
def contratos():
    contratos = Contrato.query.all()
    inquilinos = Inquilino.query.all()
    propiedades = Propiedad.query.all()
    return render_template('contratos.html', contratos=contratos, inquilinos=inquilinos, propiedades=propiedades)

@app.route('/reportes')
def reportes():
    return render_template('reportes.html')

@app.route('/importar', methods=['GET'])
def importar():
    return render_template('importar.html')

@app.route('/api/importar', methods=['POST'])
def importar_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    tipo = request.form.get('tipo')
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400

    try:
        # Crear directorio de uploads si no existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Leer CSV
        df = pd.read_csv(filepath)
        
        if tipo == 'inquilinos':
            for _, row in df.iterrows():
                inquilino = Inquilino(
                    nombre=row['nombre'],
                    dni=row['dni'],
                    email=row['email'],
                    telefono=row.get('telefono', '')
                )
                db.session.add(inquilino)
        
        elif tipo == 'propiedades':
            for _, row in df.iterrows():
                propietario = Propietario.query.filter_by(nombre=row['propietario']).first()
                if not propietario:
                    propietario = Propietario(
                        nombre=row['propietario'],
                        email=row.get('email_propietario', 'sin_email@ejemplo.com')
                    )
                    db.session.add(propietario)
                    db.session.flush()
                
                propiedad = Propiedad(
                    direccion=row['direccion'],
                    tipo=row['tipo'],
                    propietario_id=propietario.id
                )
                db.session.add(propiedad)
        
        elif tipo == 'facturas':
            for _, row in df.iterrows():
                contrato = Contrato.query.get(row['contrato_id'])
                if contrato:
                    factura = Factura(
                        fecha_emision=datetime.strptime(row['fecha_emision'], '%Y-%m-%d'),
                        monto=float(row['monto']),
                        pagado=row.get('pagado', False),
                        fecha_pago=datetime.strptime(row['fecha_pago'], '%Y-%m-%d') if row.get('fecha_pago') else None,
                        contrato_id=contrato.id
                    )
                    db.session.add(factura)
        
        db.session.commit()
        
        # Eliminar archivo después de procesarlo
        os.remove(filepath)
        
        return jsonify({'message': f'Importación de {tipo} completada con éxito'}), 200
    
    except Exception as e:
        db.session.rollback()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Error durante la importación: {str(e)}'}), 500

@app.route('/api/inquilinos', methods=['POST'])
def crear_inquilino():
    try:
        data = request.get_json()
        nuevo_inquilino = Inquilino(
            nombre=data['nombre'],
            dni=data['dni'],
            email=data['email'],
            telefono=data.get('telefono', '')
        )
        db.session.add(nuevo_inquilino)
        db.session.commit()
        return jsonify({
            'message': 'Inquilino creado exitosamente',
            'inquilino': {
                'id': nuevo_inquilino.id,
                'nombre': nuevo_inquilino.nombre,
                'dni': nuevo_inquilino.dni,
                'email': nuevo_inquilino.email,
                'telefono': nuevo_inquilino.telefono
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: inquilino.dni' in str(e):
            return jsonify({'error': 'DNI ya existe'}), 400
        if 'UNIQUE constraint failed: inquilino.email' in str(e):
            return jsonify({'error': 'Email ya existe'}), 400
        return jsonify({'error': str(e)}), 400

@app.route('/api/inquilinos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_inquilino(id):
    inquilino = Inquilino.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': inquilino.id,
            'nombre': inquilino.nombre,
            'dni': inquilino.dni,
            'email': inquilino.email,
            'telefono': inquilino.telefono
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            inquilino.nombre = data['nombre']
            inquilino.dni = data['dni']
            inquilino.email = data['email']
            inquilino.telefono = data.get('telefono', '')
            db.session.commit()
            return jsonify({'message': 'Inquilino actualizado exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(inquilino)
            db.session.commit()
            return jsonify({'message': 'Inquilino eliminado exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/propietarios', methods=['POST'])
def crear_propietario():
    try:
        data = request.get_json()
        nuevo_propietario = Propietario(
            nombre=data['nombre'],
            email=data['email']
        )
        db.session.add(nuevo_propietario)
        db.session.commit()
        return jsonify({
            'message': 'Propietario creado exitosamente',
            'id': nuevo_propietario.id,
            'nombre': nuevo_propietario.nombre,
            'email': nuevo_propietario.email
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/propiedades', methods=['POST'])
def crear_propiedad():
    try:
        data = request.get_json()
        nueva_propiedad = Propiedad(
            direccion=data['direccion'],
            tipo=data['tipo'],
            propietario_id=data['propietario_id']
        )
        db.session.add(nueva_propiedad)
        db.session.commit()
        return jsonify({
            'message': 'Propiedad creada exitosamente',
            'propiedad': {
                'id': nueva_propiedad.id,
                'direccion': nueva_propiedad.direccion,
                'tipo': nueva_propiedad.tipo,
                'propietario_id': nueva_propiedad.propietario_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/propiedades/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_propiedad(id):
    propiedad = Propiedad.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': propiedad.id,
            'direccion': propiedad.direccion,
            'tipo': propiedad.tipo,
            'propietario_nombre': propiedad.propietario.nombre,
            'propietario_email': propiedad.propietario.email
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            propiedad.direccion = data['direccion']
            propiedad.tipo = data['tipo']
            
            # Actualizar propietario
            propietario = propiedad.propietario
            propietario.nombre = data['propietario_nombre']
            propietario.email = data['propietario_email']
            
            db.session.commit()
            return jsonify({'message': 'Propiedad actualizada exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(propiedad)
            db.session.commit()
            return jsonify({'message': 'Propiedad eliminada exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/contratos', methods=['POST'])
def crear_contrato():
    try:
        data = request.get_json()
        nuevo_contrato = Contrato(
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d'),
            fecha_fin=datetime.strptime(data['fecha_fin'], '%Y-%m-%d'),
            monto_mensual=float(data['monto_mensual']),
            inquilino_id=data['inquilino_id'],
            propiedad_id=data['propiedad_id']
        )
        db.session.add(nuevo_contrato)
        db.session.commit()
        return jsonify({'message': 'Contrato creado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/contratos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': contrato.id,
            'fecha_inicio': contrato.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': contrato.fecha_fin.strftime('%Y-%m-%d'),
            'monto_mensual': contrato.monto_mensual,
            'activo': contrato.activo,
            'inquilino_id': contrato.inquilino_id,
            'propiedad_id': contrato.propiedad_id
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            contrato.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
            contrato.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
            contrato.monto_mensual = float(data['monto_mensual'])
            contrato.activo = data.get('activo', True)
            contrato.inquilino_id = data['inquilino_id']
            contrato.propiedad_id = data['propiedad_id']
            
            db.session.commit()
            return jsonify({'message': 'Contrato actualizado exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(contrato)
            db.session.commit()
            return jsonify({'message': 'Contrato eliminado exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/facturas', methods=['POST'])
def crear_factura():
    try:
        data = request.get_json()
        nueva_factura = Factura(
            fecha_emision=datetime.strptime(data['fecha_emision'], '%Y-%m-%d'),
            monto=float(data['monto']),
            pagado=data.get('pagado', False),
            fecha_pago=datetime.strptime(data['fecha_pago'], '%Y-%m-%d') if data.get('fecha_pago') else None,
            contrato_id=data['contrato_id']
        )
        db.session.add(nueva_factura)
        db.session.commit()
        return jsonify({
            'message': 'Factura creada exitosamente',
            'factura': {
                'id': nueva_factura.id,
                'fecha_emision': nueva_factura.fecha_emision.strftime('%Y-%m-%d'),
                'monto': nueva_factura.monto,
                'pagado': nueva_factura.pagado,
                'fecha_pago': nueva_factura.fecha_pago.strftime('%Y-%m-%d') if nueva_factura.fecha_pago else None
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/facturas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def gestionar_factura(id):
    factura = Factura.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify({
            'id': factura.id,
            'fecha_emision': factura.fecha_emision.strftime('%Y-%m-%d'),
            'monto': factura.monto,
            'pagado': factura.pagado,
            'fecha_pago': factura.fecha_pago.strftime('%Y-%m-%d') if factura.fecha_pago else None,
            'contrato_id': factura.contrato_id
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            factura.fecha_emision = datetime.strptime(data['fecha_emision'], '%Y-%m-%d')
            factura.monto = float(data['monto'])
            factura.pagado = data.get('pagado', False)
            factura.fecha_pago = datetime.strptime(data['fecha_pago'], '%Y-%m-%d') if data.get('fecha_pago') else None
            factura.contrato_id = data['contrato_id']
            
            db.session.commit()
            return jsonify({'message': 'Factura actualizada exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(factura)
            db.session.commit()
            return jsonify({'message': 'Factura eliminada exitosamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/reporte-facturacion', methods=['POST'])
def reporte_facturacion():
    try:
        data = request.get_json()
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
        tipo = data.get('tipo', 'contabilidad')  # 'contabilidad' o 'morosidad'

        # Base query
        query = db.session.query(
            Factura.id,
            Factura.fecha_emision,
            Factura.monto,
            Factura.pagado,
            Factura.fecha_pago,
            Contrato.monto_mensual,
            Inquilino.nombre.label('inquilino_nombre'),
            Inquilino.dni,
            Propiedad.direccion,
            Propietario.nombre.label('propietario_nombre')
        ).join(
            Contrato, Factura.contrato_id == Contrato.id
        ).join(
            Inquilino, Contrato.inquilino_id == Inquilino.id
        ).join(
            Propiedad, Contrato.propiedad_id == Propiedad.id
        ).join(
            Propietario, Propiedad.propietario_id == Propietario.id
        ).filter(
            Factura.fecha_emision >= fecha_inicio,
            Factura.fecha_emision <= fecha_fin
        )

        if tipo == 'morosidad':
            query = query.filter(Factura.pagado == False)

        facturas = query.all()
        
        result = []
        for f in facturas:
            result.append({
                'id': f.id,
                'fecha_emision': f.fecha_emision.strftime('%Y-%m-%d'),
                'monto': f.monto,
                'pagado': f.pagado,
                'fecha_pago': f.fecha_pago.strftime('%Y-%m-%d') if f.fecha_pago else None,
                'monto_mensual': f.monto_mensual,
                'inquilino_nombre': f.inquilino_nombre,
                'dni': f.dni,
                'direccion': f.direccion,
                'propietario_nombre': f.propietario_nombre
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Crear datos de prueba si la base de datos está vacía
        if not Inquilino.query.first():
            # Crear propietario de prueba
            propietario = Propietario(nombre='Juan Pérez', email='juan@example.com')
            db.session.add(propietario)
            db.session.flush()
            
            # Crear propiedad de prueba
            propiedad = Propiedad(
                direccion='Av. Principal 123',
                tipo='Casa',
                propietario_id=propietario.id
            )
            db.session.add(propiedad)
            db.session.flush()
            
            # Crear inquilino de prueba
            inquilino = Inquilino(
                nombre='María García',
                dni='12345678',
                email='maria@example.com',
                telefono='555-1234'
            )
            db.session.add(inquilino)
            db.session.flush()
            
            # Crear contrato de prueba
            contrato = Contrato(
                fecha_inicio=datetime(2024, 1, 1),
                fecha_fin=datetime(2024, 12, 31),
                monto_mensual=1500.0,
                activo=True,
                inquilino_id=inquilino.id,
                propiedad_id=propiedad.id
            )
            db.session.add(contrato)
            db.session.flush()
            
            # Crear algunas facturas de prueba
            for mes in range(1, 3):  # Facturas para enero y febrero
                factura = Factura(
                    fecha_emision=datetime(2024, mes, 1),
                    monto=1500.0,
                    pagado=mes == 1,  # La factura de enero está pagada
                    fecha_pago=datetime(2024, mes, 5) if mes == 1 else None,
                    contrato_id=contrato.id
                )
                db.session.add(factura)
            
            db.session.commit()
            
    app.run(debug=True, port=5002)
