from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Factura, Contrato, db
from app.forms.factura_forms import FacturaForm
from datetime import datetime

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/lista')
@login_required
def lista():
    facturas = Factura.query.order_by(Factura.fecha_emision.desc()).all()
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
            contrato_id=form.contrato_id.data
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
        db.session.commit()
        flash('Factura actualizada exitosamente.')
        return redirect(url_for('facturas.lista'))
    
    return render_template('facturas/editar.html', form=form, factura=factura)

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
