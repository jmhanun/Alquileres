from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models import Propietario, db
from app.forms.propietario_forms import PropietarioForm

propietarios_bp = Blueprint('propietarios', __name__)

@propietarios_bp.route('/lista')
@login_required
def lista():
    propietarios = Propietario.query.all()
    return render_template('propietarios/lista.html', propietarios=propietarios)

@propietarios_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = PropietarioForm()
    
    if form.validate_on_submit():
        propietario = Propietario(
            nombre=form.nombre.data,
            dni=form.dni.data,
            email=form.email.data,
            telefono=form.telefono.data
        )
        db.session.add(propietario)
        db.session.commit()
        flash('Propietario creado exitosamente.')
        return redirect(url_for('propietarios.lista'))
    
    return render_template('propietarios/crear.html', form=form)

@propietarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    propietario = Propietario.query.get_or_404(id)
    form = PropietarioForm(obj=propietario)
    
    if form.validate_on_submit():
        propietario.nombre = form.nombre.data
        propietario.dni = form.dni.data
        propietario.email = form.email.data
        propietario.telefono = form.telefono.data
        db.session.commit()
        flash('Propietario actualizado exitosamente.')
        return redirect(url_for('propietarios.lista'))
    
    return render_template('propietarios/editar.html', form=form, propietario=propietario)

@propietarios_bp.route('/ver/<int:id>')
@login_required
def ver(id):
    propietario = Propietario.query.get_or_404(id)
    return render_template('propietarios/ver.html', propietario=propietario)

@propietarios_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    propietario = Propietario.query.get_or_404(id)
    db.session.delete(propietario)
    db.session.commit()
    flash('Propietario eliminado exitosamente.')
    return redirect(url_for('propietarios.lista'))
