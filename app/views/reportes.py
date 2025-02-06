from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from app.models import Factura, Contrato, Propiedad, Inquilino
from sqlalchemy import func
import pandas as pd
from io import BytesIO
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales
    total_propiedades = Propiedad.query.count()
    total_inquilinos = Inquilino.query.count()
    contratos_activos = Contrato.query.filter_by(activo=True).count()
    facturas_pendientes = Factura.query.filter_by(pagado=False).count()
    
    # Ingresos mensuales
    ingresos_mes = db.session.query(
        func.strftime('%Y-%m', Factura.fecha_pago).label('mes'),
        func.sum(Factura.monto).label('total')
    ).filter(
        Factura.pagado == True
    ).group_by('mes').order_by('mes').all()
    
    # Morosidad por inquilino
    morosidad = db.session.query(
        Inquilino.nombre,
        func.count(Factura.id).label('facturas_pendientes'),
        func.sum(Factura.monto).label('monto_pendiente')
    ).join(
        Contrato, Factura.contrato_id == Contrato.id
    ).join(
        Inquilino, Contrato.inquilino_id == Inquilino.id
    ).filter(
        Factura.pagado == False
    ).group_by(Inquilino.id).all()
    
    return render_template('reportes/dashboard.html',
                         total_propiedades=total_propiedades,
                         total_inquilinos=total_inquilinos,
                         contratos_activos=contratos_activos,
                         facturas_pendientes=facturas_pendientes,
                         ingresos_mes=ingresos_mes,
                         morosidad=morosidad)

@reportes_bp.route('/facturacion')
@login_required
def facturacion():
    fecha_inicio = request.args.get('fecha_inicio', 
                                  datetime.now().replace(day=1).strftime('%Y-%m-%d'))
    fecha_fin = request.args.get('fecha_fin', 
                               datetime.now().strftime('%Y-%m-%d'))
    
    facturas = Factura.query.filter(
        Factura.fecha_emision.between(fecha_inicio, fecha_fin)
    ).order_by(Factura.fecha_emision).all()
    
    # Calcular totales
    total_facturado = sum(f.monto for f in facturas)
    total_cobrado = sum(f.monto for f in facturas if f.pagado)
    total_pendiente = total_facturado - total_cobrado
    
    return render_template('reportes/facturacion.html',
                         facturas=facturas,
                         fecha_inicio=fecha_inicio,
                         fecha_fin=fecha_fin,
                         total_facturado=total_facturado,
                         total_cobrado=total_cobrado,
                         total_pendiente=total_pendiente)

@reportes_bp.route('/exportar_excel')
@login_required
def exportar_excel():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Consulta de facturas
    facturas = Factura.query.filter(
        Factura.fecha_emision.between(fecha_inicio, fecha_fin)
    ).all()
    
    # Crear DataFrame
    data = []
    for f in facturas:
        data.append({
            'Fecha Emisión': f.fecha_emision,
            'Inquilino': f.contrato.inquilino.nombre,
            'Propiedad': f.contrato.propiedad.direccion,
            'Monto': f.monto,
            'Estado': 'Pagado' if f.pagado else 'Pendiente',
            'Fecha Pago': f.fecha_pago
        })
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Facturas')
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'reporte_facturacion_{fecha_inicio}_{fecha_fin}.xlsx'
    )
