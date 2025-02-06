from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Contrato, Propiedad, Inquilino, db
from app.forms.contrato_forms import ContratoForm
from datetime import datetime

contratos_bp = Blueprint('contratos', __name__)

@contratos_bp.route('/lista')
@login_required
def lista():
    contratos = Contrato.query.all()
    return render_template('contratos/lista.html', contratos=contratos)

@contratos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = ContratoForm()
    form.propiedad_id.choices = [(p.id, p.direccion) for p in Propiedad.query.all()]
    form.inquilino_id.choices = [(i.id, i.nombre) for i in Inquilino.query.all()]
    
    if form.validate_on_submit():
        # Verificar si la propiedad ya tiene un contrato activo
        contrato_activo = Contrato.query.filter_by(
            propiedad_id=form.propiedad_id.data,
            activo=True
        ).first()
        
        if contrato_activo:
            flash('La propiedad ya tiene un contrato activo.')
            return render_template('contratos/crear.html', form=form)
        
        contrato = Contrato(
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin=form.fecha_fin.data,
            monto_mensual=form.monto_mensual.data,
            deposito=form.deposito.data,
            notas=form.notas.data,
            propiedad_id=form.propiedad_id.data,
            inquilino_id=form.inquilino_id.data,
            activo=True
        )
        db.session.add(contrato)
        db.session.commit()
        flash('Contrato creado exitosamente.')
        return redirect(url_for('contratos.lista'))
    
    return render_template('contratos/crear.html', form=form)

@contratos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    contrato = Contrato.query.get_or_404(id)
    form = ContratoForm(obj=contrato)
    form.propiedad_id.choices = [(p.id, p.direccion) for p in Propiedad.query.all()]
    form.inquilino_id.choices = [(i.id, i.nombre) for i in Inquilino.query.all()]
    
    if form.validate_on_submit():
        contrato.fecha_inicio = form.fecha_inicio.data
        contrato.fecha_fin = form.fecha_fin.data
        contrato.monto_mensual = form.monto_mensual.data
        contrato.deposito = form.deposito.data
        contrato.notas = form.notas.data
        contrato.propiedad_id = form.propiedad_id.data
        contrato.inquilino_id = form.inquilino_id.data
        db.session.commit()
        flash('Contrato actualizado exitosamente.')
        return redirect(url_for('contratos.lista'))
    
    return render_template('contratos/editar.html', form=form, contrato=contrato)

@contratos_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    contrato = Contrato.query.get_or_404(id)
    return render_template('contratos/ver.html', contrato=contrato)

@contratos_bp.route('/finalizar/<int:id>')
@login_required
def finalizar(id):
    contrato = Contrato.query.get_or_404(id)
    if not contrato.activo:
        flash('El contrato ya está finalizado.')
        return redirect(url_for('contratos.lista'))
    
    contrato.activo = False
    contrato.fecha_fin = datetime.now().date()
    db.session.commit()
    flash('Contrato finalizado exitosamente.')
    return redirect(url_for('contratos.lista'))
