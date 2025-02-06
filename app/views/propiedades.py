from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Propiedad, Propietario, db
from app.forms.propiedad_forms import PropiedadForm

propiedades_bp = Blueprint('propiedades', __name__)

@propiedades_bp.route('/lista')
@login_required
def lista():
    propiedades = Propiedad.query.all()
    return render_template('propiedades/lista.html', propiedades=propiedades)

@propiedades_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = PropiedadForm()
    form.propietario_id.choices = [(p.id, p.nombre) for p in Propietario.query.all()]
    
    if form.validate_on_submit():
        propiedad = Propiedad(
            direccion=form.direccion.data,
            tipo=form.tipo.data,
            descripcion=form.descripcion.data,
            propietario_id=form.propietario_id.data
        )
        db.session.add(propiedad)
        db.session.commit()
        flash('Propiedad creada exitosamente.')
        return redirect(url_for('propiedades.lista'))
    
    return render_template('propiedades/crear.html', form=form)

@propiedades_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    propiedad = Propiedad.query.get_or_404(id)
    form = PropiedadForm(obj=propiedad)
    form.propietario_id.choices = [(p.id, p.nombre) for p in Propietario.query.all()]
    
    if form.validate_on_submit():
        propiedad.direccion = form.direccion.data
        propiedad.tipo = form.tipo.data
        propiedad.descripcion = form.descripcion.data
        propiedad.propietario_id = form.propietario_id.data
        db.session.commit()
        flash('Propiedad actualizada exitosamente.')
        return redirect(url_for('propiedades.lista'))
    
    return render_template('propiedades/editar.html', form=form, propiedad=propiedad)

@propiedades_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    propiedad = Propiedad.query.get_or_404(id)
    return render_template('propiedades/ver.html', propiedad=propiedad)

@propiedades_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    propiedad = Propiedad.query.get_or_404(id)
    if propiedad.contratos:
        flash('No se puede eliminar una propiedad con contratos asociados.')
        return redirect(url_for('propiedades.lista'))
    
    db.session.delete(propiedad)
    db.session.commit()
    flash('Propiedad eliminada exitosamente.')
    return redirect(url_for('propiedades.lista'))
