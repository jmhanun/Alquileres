from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from app.models import Factura, Contrato, db
from app.forms.factura_forms import FacturaForm
from datetime import datetime
import pandas as pd
import io

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/lista')
@login_required
def lista():
    estado = request.args.get('estado')
    mes = request.args.get('mes')
    
    query = Factura.query
    
    if estado:
        if estado == 'pendiente':
            query = query.filter_by(pagado=False)
        elif estado == 'pagada':
            query = query.filter_by(pagado=True)
    
    if mes:
        try:
            fecha = datetime.strptime(mes + '-01', '%Y-%m-%d')
            query = query.filter(
                db.extract('year', Factura.fecha_emision) == fecha.year,
                db.extract('month', Factura.fecha_emision) == fecha.month
            )
        except ValueError:
            flash('Formato de fecha inválido', 'error')
    
    facturas = query.order_by(Factura.fecha_emision.desc()).all()
    return render_template('facturas/lista.html', facturas=facturas)

@facturas_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = FacturaForm()
    form.contrato_id.choices = [(c.id, f"{c.propiedad.direccion} - {c.inquilino.nombre}") 
                               for c in Contrato.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        factura = Factura(
            fecha_emision=form.fecha_emision.data,
            monto=form.monto.data,
            contrato_id=form.contrato_id.data,
            pagado=form.pagado.data,
            fecha_pago=form.fecha_pago.data if form.pagado.data else None
        )
        db.session.add(factura)
        db.session.commit()
        flash('Factura creada exitosamente.')
        return redirect(url_for('facturas.lista'))
    
    return render_template('facturas/crear.html', form=form)

@facturas_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    factura = Factura.query.get_or_404(id)
    if factura.pagado:
        flash('No se puede editar una factura pagada.')
        return redirect(url_for('facturas.lista'))
    
    form = FacturaForm(obj=factura)
    form.contrato_id.choices = [(c.id, f"{c.propiedad.direccion} - {c.inquilino.nombre}") 
                               for c in Contrato.query.all()]
    
    if form.validate_on_submit():
        factura.fecha_emision = form.fecha_emision.data
        factura.monto = form.monto.data
        factura.contrato_id = form.contrato_id.data
        factura.pagado = form.pagado.data
        factura.fecha_pago = form.fecha_pago.data if form.pagado.data else None
        
        db.session.commit()
        flash('Factura actualizada exitosamente.')
        return redirect(url_for('facturas.lista'))
    
    return render_template('facturas/editar.html', form=form, factura=factura)

@facturas_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    factura = Factura.query.get_or_404(id)
    return render_template('facturas/ver.html', factura=factura)

@facturas_bp.route('/registrar_pago/<int:id>')
@login_required
def registrar_pago(id):
    factura = Factura.query.get_or_404(id)
    if factura.pagado:
        flash('La factura ya está pagada.')
        return redirect(url_for('facturas.lista'))
    
    factura.pagado = True
    factura.fecha_pago = datetime.now().date()
    db.session.commit()
    flash('Pago registrado exitosamente.')
    return redirect(url_for('facturas.lista'))

@facturas_bp.route('/anular_pago/<int:id>')
@login_required
def anular_pago(id):
    factura = Factura.query.get_or_404(id)
    if not factura.pagado:
        flash('La factura no está pagada.')
        return redirect(url_for('facturas.lista'))
    
    factura.pagado = False
    factura.fecha_pago = None
    db.session.commit()
    flash('Pago anulado exitosamente.')
    return redirect(url_for('facturas.lista'))

@facturas_bp.route('/generar_reporte')
@login_required
def generar_reporte():
    estado = request.args.get('estado')
    mes = request.args.get('mes')
    
    query = Factura.query
    
    if estado:
        if estado == 'pendiente':
            query = query.filter_by(pagado=False)
        elif estado == 'pagada':
            query = query.filter_by(pagado=True)
    
    if mes:
        try:
            fecha = datetime.strptime(mes + '-01', '%Y-%m-%d')
            query = query.filter(
                db.extract('year', Factura.fecha_emision) == fecha.year,
                db.extract('month', Factura.fecha_emision) == fecha.month
            )
        except ValueError:
            flash('Formato de fecha inválido', 'error')
            return redirect(url_for('facturas.lista'))
    
    facturas = query.order_by(Factura.fecha_emision.desc()).all()
    
    # Crear DataFrame con los datos
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
    output = io.BytesIO()
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
