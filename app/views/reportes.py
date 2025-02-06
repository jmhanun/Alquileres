from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from app.models import Factura, Contrato, Propiedad, Inquilino
from app import db
from sqlalchemy import func, extract
import pandas as pd
from io import BytesIO
from datetime import datetime, date, timedelta

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/dashboard')
@login_required
def dashboard():
    # Estadísticas generales
    total_propiedades = Propiedad.query.count()
    total_inquilinos = Inquilino.query.count()
    contratos_activos = Contrato.query.filter_by(activo=True).count()
    facturas_pendientes = Factura.query.filter_by(pagado=False).count()
    
    # Calcular ingresos del mes actual
    hoy = datetime.now()
    primer_dia_mes = datetime(hoy.year, hoy.month, 1)
    ingresos_mes = db.session.query(
        func.sum(Factura.monto)
    ).filter(
        Factura.pagado == True,
        Factura.fecha_pago >= primer_dia_mes
    ).scalar() or 0
    
    # Propiedades disponibles
    propiedades_disponibles = Propiedad.query.filter(
        ~Propiedad.id.in_(
            db.session.query(Contrato.propiedad_id).filter_by(activo=True)
        )
    ).count()
    
    # Propiedades alquiladas
    propiedades_alquiladas = total_propiedades - propiedades_disponibles
    
    # Datos para el gráfico de ingresos
    ultimos_6_meses = []
    datos_ingresos = []
    labels_ingresos = []
    
    for i in range(5, -1, -1):
        mes = hoy - timedelta(days=30*i)
        primer_dia = datetime(mes.year, mes.month, 1)
        ultimo_dia = (datetime(mes.year, mes.month + 1, 1) if mes.month < 12 
                     else datetime(mes.year + 1, 1, 1)) - timedelta(days=1)
        
        ingresos = db.session.query(
            func.sum(Factura.monto)
        ).filter(
            Factura.pagado == True,
            Factura.fecha_pago >= primer_dia,
            Factura.fecha_pago <= ultimo_dia
        ).scalar() or 0
        
        datos_ingresos.append(ingresos)
        labels_ingresos.append(mes.strftime('%B %Y'))
        ultimos_6_meses.append(primer_dia)
    
    # Contratos por vencer (próximos 30 días)
    contratos_por_vencer = Contrato.query.filter(
        Contrato.activo == True,
        Contrato.fecha_fin <= hoy + timedelta(days=30)
    ).order_by(Contrato.fecha_fin).all()
    
    # Últimos pagos
    ultimos_pagos = Factura.query.filter_by(
        pagado=True
    ).order_by(
        Factura.fecha_pago.desc()
    ).limit(5).all()
    
    return render_template('reportes/dashboard.html',
                         total_propiedades=total_propiedades,
                         total_inquilinos=total_inquilinos,
                         contratos_activos=contratos_activos,
                         facturas_pendientes=facturas_pendientes,
                         ingresos_mes=ingresos_mes,
                         propiedades_disponibles=propiedades_disponibles,
                         propiedades_alquiladas=propiedades_alquiladas,
                         labels_ingresos=labels_ingresos,
                         datos_ingresos=datos_ingresos,
                         contratos_por_vencer=contratos_por_vencer,
                         ultimos_pagos=ultimos_pagos)

@reportes_bp.route('/facturacion')
@login_required
def facturacion():
    # Obtener parámetros de filtro
    mes = request.args.get('mes', datetime.now().strftime('%Y-%m'))
    try:
        fecha = datetime.strptime(mes + '-01', '%Y-%m-%d')
    except ValueError:
        fecha = datetime.now().replace(day=1)
    
    # Estadísticas de facturación del mes
    facturas_mes = Factura.query.filter(
        extract('year', Factura.fecha_emision) == fecha.year,
        extract('month', Factura.fecha_emision) == fecha.month
    )
    
    total_facturado = facturas_mes.with_entities(
        func.sum(Factura.monto)
    ).scalar() or 0
    
    total_cobrado = facturas_mes.filter_by(
        pagado=True
    ).with_entities(
        func.sum(Factura.monto)
    ).scalar() or 0
    
    total_pendiente = total_facturado - total_cobrado
    
    # Detalle de facturas del mes
    facturas = facturas_mes.order_by(Factura.fecha_emision.desc()).all()
    
    return render_template('reportes/facturacion.html',
                         mes=mes,
                         total_facturado=total_facturado,
                         total_cobrado=total_cobrado,
                         total_pendiente=total_pendiente,
                         facturas=facturas)

@reportes_bp.route('/exportar_excel')
@login_required
def exportar_excel():
    # Obtener datos
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
    
    # Crear DataFrame
    data = []
    for factura in facturas:
        data.append({
            'Fecha Emisión': factura.fecha_emision.strftime('%d/%m/%Y'),
            'Inquilino': factura.contrato.inquilino.nombre,
            'Propiedad': factura.contrato.propiedad.direccion,
            'Monto': factura.monto,
            'Estado': 'Pagada' if factura.pagado else 'Pendiente',
            'Fecha Pago': factura.fecha_pago.strftime('%d/%m/%Y') if factura.fecha_pago else '-'
        })
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Facturas')
    output.seek(0)
    
    # Generar nombre del archivo
    filename = f'reporte_facturas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@reportes_bp.route('/reporte_anual')
@login_required
def reporte_anual():
    # Obtener el año del parámetro o usar el año actual
    try:
        anio = int(request.args.get('anio', date.today().year))
    except (ValueError, TypeError):
        anio = date.today().year

    # Nombres de los meses en español
    nombres_meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]

    # Obtener todas las facturas del año
    facturas_anio = Factura.query.filter(
        extract('year', Factura.fecha_emision) == anio
    )

    # Calcular totales por mes
    datos_mensuales = []
    total_anual = 0.0
    total_cobrado_anual = 0.0
    total_pendiente_anual = 0.0

    for mes in range(1, 13):
        facturas_mes = facturas_anio.filter(
            extract('month', Factura.fecha_emision) == mes
        )
        
        total_mes = facturas_mes.with_entities(
            func.coalesce(func.sum(Factura.monto), 0.0)
        ).scalar()
        
        cobrado_mes = facturas_mes.filter_by(
            pagado=True
        ).with_entities(
            func.coalesce(func.sum(Factura.monto), 0.0)
        ).scalar()
        
        pendiente_mes = total_mes - cobrado_mes
        
        datos_mensuales.append({
            'mes': nombres_meses[mes - 1],
            'total': float(total_mes),
            'cobrado': float(cobrado_mes),
            'pendiente': float(pendiente_mes)
        })
        
        total_anual += total_mes
        total_cobrado_anual += cobrado_mes
        total_pendiente_anual += pendiente_mes

    # Obtener años disponibles para el selector de una manera más segura
    anos_query = db.session.query(
        func.distinct(func.strftime('%Y', Factura.fecha_emision))
    ).filter(
        Factura.fecha_emision.isnot(None)
    ).order_by(
        func.strftime('%Y', Factura.fecha_emision).desc()
    ).all()

    # Convertir los resultados a enteros y asegurar que el año actual esté incluido
    anos_disponibles = []
    anos_set = set()
    
    # Agregar el año actual primero
    anos_disponibles.append(anio)
    anos_set.add(anio)
    
    # Agregar los años de la consulta
    for ano in anos_query:
        try:
            year = int(ano[0]) if ano[0] else None
            if year and year not in anos_set:
                anos_disponibles.append(year)
                anos_set.add(year)
        except (ValueError, TypeError):
            continue
    
    # Ordenar los años de más reciente a más antiguo
    anos_disponibles.sort(reverse=True)

    return render_template('reportes/reporte_anual.html',
                         anio=anio,
                         anos_disponibles=anos_disponibles,
                         datos_mensuales=datos_mensuales,
                         total_anual=float(total_anual),
                         total_cobrado_anual=float(total_cobrado_anual),
                         total_pendiente_anual=float(total_pendiente_anual))
