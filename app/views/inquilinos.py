from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Inquilino, db
from app.forms.inquilino_forms import InquilinoForm

inquilinos_bp = Blueprint('inquilinos', __name__)

@inquilinos_bp.route('/lista')
@login_required
def lista():
    inquilinos = Inquilino.query.all()
    return render_template('inquilinos/lista.html', inquilinos=inquilinos)

@inquilinos_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = InquilinoForm()
    if form.validate_on_submit():
        inquilino = Inquilino(
            nombre=form.nombre.data,
            dni=form.dni.data,
            email=form.email.data,
            telefono=form.telefono.data
        )
        db.session.add(inquilino)
        try:
            db.session.commit()
            flash('Inquilino creado exitosamente.')
            return redirect(url_for('inquilinos.lista'))
        except Exception as e:
            db.session.rollback()
            flash('Error al crear el inquilino. El DNI o email ya existe.')
            return render_template('inquilinos/crear.html', form=form)
    
    return render_template('inquilinos/crear.html', form=form)

@inquilinos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    inquilino = Inquilino.query.get_or_404(id)
    form = InquilinoForm(obj=inquilino)
    
    if form.validate_on_submit():
        inquilino.nombre = form.nombre.data
        inquilino.dni = form.dni.data
        inquilino.email = form.email.data
        inquilino.telefono = form.telefono.data
        try:
            db.session.commit()
            flash('Inquilino actualizado exitosamente.')
            return redirect(url_for('inquilinos.lista'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar el inquilino. El DNI o email ya existe.')
            return render_template('inquilinos/editar.html', form=form, inquilino=inquilino)
    
    return render_template('inquilinos/editar.html', form=form, inquilino=inquilino)

@inquilinos_bp.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    inquilino = Inquilino.query.get_or_404(id)
    if inquilino.contratos:
        flash('No se puede eliminar un inquilino con contratos asociados.')
        return redirect(url_for('inquilinos.lista'))
    
    db.session.delete(inquilino)
    db.session.commit()
    flash('Inquilino eliminado exitosamente.')
    return redirect(url_for('inquilinos.lista'))
