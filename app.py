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

@app.route('/api/reporte-facturacion', methods=['GET', 'POST'])
def reporte_facturacion():
    if request.method == 'GET':
        fecha_inicio = datetime.strptime(request.args.get('fecha_inicio'), '%Y-%m-%d')
        fecha_fin = datetime.strptime(request.args.get('fecha_fin'), '%Y-%m-%d')
        tipo_reporte = request.args.get('tipo')
        formato = request.args.get('formato', 'json')
    else:  # POST
        data = request.get_json()
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
        fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
        tipo_reporte = data['tipo']
        formato = data.get('formato', 'json')

    if tipo_reporte == 'contabilidad':
        # Consulta para el reporte contable
        resultados = db.session.query(
            Factura.fecha_emision,
            Factura.monto,
            Factura.pagado,
            Factura.fecha_pago,
            Contrato.monto_mensual,
            Inquilino.nombre.label('inquilino_nombre'),
            Inquilino.dni.label('inquilino_dni'),
            Propiedad.direccion.label('propiedad_direccion'),
            Propiedad.tipo.label('propiedad_tipo'),
            func.extract('year', Factura.fecha_emision).label('anio')
        ).join(Contrato, Factura.contrato_id == Contrato.id)\
         .join(Inquilino, Contrato.inquilino_id == Inquilino.id)\
         .join(Propiedad, Contrato.propiedad_id == Propiedad.id)\
         .filter(Factura.fecha_emision.between(fecha_inicio, fecha_fin))\
         .order_by(func.extract('year', Factura.fecha_emision),
                  Propiedad.direccion,
                  Inquilino.nombre,
                  Factura.fecha_emision)\
         .all()

        # Procesar los resultados para el formato contable
        data_list = []
        saldo_acumulado = 0
        
        for r in resultados:
            # Entrada para la factura (débito)
            saldo_acumulado += r.monto
            data_list.append({
                'fecha': r.fecha_emision.strftime('%d/%m/%Y'),
                'descripcion': f'Factura - {r.propiedad_direccion} - {r.inquilino_nombre} (DNI: {r.inquilino_dni})',
                'debito': float(r.monto),
                'credito': 0,
                'saldo': saldo_acumulado,
                'anio': r.anio,
                'propiedad': r.propiedad_direccion,
                'tipo_propiedad': r.propiedad_tipo,
                'inquilino': r.inquilino_nombre,
                'dni': r.inquilino_dni
            })
            
            # Si la factura está pagada, agregar el pago (crédito)
            if r.pagado:
                saldo_acumulado -= r.monto
                data_list.append({
                    'fecha': r.fecha_pago.strftime('%d/%m/%Y'),
                    'descripcion': f'Pago - {r.propiedad_direccion} - {r.inquilino_nombre} (DNI: {r.inquilino_dni})',
                    'debito': 0,
                    'credito': float(r.monto),
                    'saldo': saldo_acumulado,
                    'anio': r.anio,
                    'propiedad': r.propiedad_direccion,
                    'tipo_propiedad': r.propiedad_tipo,
                    'inquilino': r.inquilino_nombre,
                    'dni': r.inquilino_dni
                })

        if formato == 'csv':
            if not data_list:
                return jsonify({'error': 'No hay datos para exportar'}), 404
                
            df = pd.DataFrame(data_list)
            # Ordenar las columnas para el CSV
            columns = ['fecha', 'anio', 'propiedad', 'tipo_propiedad', 'inquilino', 'dni', 
                      'descripcion', 'debito', 'credito', 'saldo']
            df = df[columns]
            csv_data = df.to_csv(index=False)
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename=reporte_contable_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.csv"}
            )
        
        return jsonify(data_list)
    
    elif tipo_reporte == 'inquilino':
        resultados = db.session.query(
            Inquilino.nombre,
            Inquilino.dni,
            func.count(Factura.id).label('cantidad_facturas'),
            func.sum(Factura.monto).label('total_facturado'),
            func.sum(case((Factura.pagado == True, Factura.monto), else_=0)).label('total_pagado')
        ).join(Contrato, Inquilino.id == Contrato.inquilino_id)\
         .join(Factura, Contrato.id == Factura.contrato_id)\
         .filter(Factura.fecha_emision.between(fecha_inicio, fecha_fin))\
         .group_by(Inquilino.id, Inquilino.nombre, Inquilino.dni)\
         .all()
        
        data_list = [{
            'nombre': r.nombre,
            'dni': r.dni,
            'cantidad_facturas': r.cantidad_facturas,
            'total_facturado': float(r.total_facturado or 0),
            'total_pagado': float(r.total_pagado or 0),
            'total_pendiente': float((r.total_facturado or 0) - (r.total_pagado or 0))
        } for r in resultados]

        if formato == 'csv':
            if not data_list:
                return jsonify({'error': 'No hay datos para exportar'}), 404
                
            df = pd.DataFrame(data_list)
            csv_data = df.to_csv(index=False)
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename=reporte_inquilinos_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.csv"}
            )
        
        return jsonify(data_list)
    
    else:  # tipo_reporte == 'propiedad'
        resultados = db.session.query(
            Propiedad.direccion,
            Propiedad.tipo,
            func.count(Factura.id).label('cantidad_facturas'),
            func.sum(Factura.monto).label('total_facturado'),
            func.sum(case((Factura.pagado == True, Factura.monto), else_=0)).label('total_pagado')
        ).join(Contrato, Propiedad.id == Contrato.propiedad_id)\
         .join(Factura, Contrato.id == Factura.contrato_id)\
         .filter(Factura.fecha_emision.between(fecha_inicio, fecha_fin))\
         .group_by(Propiedad.id, Propiedad.direccion, Propiedad.tipo)\
         .all()
        
        data_list = [{
            'direccion': r.direccion,
            'tipo': r.tipo,
            'cantidad_facturas': r.cantidad_facturas,
            'total_facturado': float(r.total_facturado or 0),
            'total_pagado': float(r.total_pagado or 0),
            'total_pendiente': float((r.total_facturado or 0) - (r.total_pagado or 0))
        } for r in resultados]

        if formato == 'csv':
            if not data_list:
                return jsonify({'error': 'No hay datos para exportar'}), 404
                
            df = pd.DataFrame(data_list)
            csv_data = df.to_csv(index=False)
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename=reporte_propiedades_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.csv"}
            )
        
        return jsonify(data_list)

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

@app.route('/api/propiedades', methods=['POST'])
def crear_propiedad():
    try:
        data = request.get_json()
        # Buscar o crear propietario
        propietario = Propietario.query.filter_by(nombre=data['propietario_nombre']).first()
        if not propietario:
            propietario = Propietario(
                nombre=data['propietario_nombre'],
                email=data['propietario_email']
            )
            db.session.add(propietario)
            db.session.flush()

        nueva_propiedad = Propiedad(
            direccion=data['direccion'],
            tipo=data['tipo'],
            propietario_id=propietario.id
        )
        db.session.add(nueva_propiedad)
        db.session.commit()
        return jsonify({
            'message': 'Propiedad creada exitosamente',
            'propiedad': {
                'id': nueva_propiedad.id,
                'direccion': nueva_propiedad.direccion,
                'tipo': nueva_propiedad.tipo,
                'propietario': propietario.nombre
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
