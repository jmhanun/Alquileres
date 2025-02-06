from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Propiedad, Inquilino, Contrato

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    propiedades = Propiedad.query.count()
    inquilinos = Inquilino.query.count()
    contratos_activos = Contrato.query.filter_by(activo=True).count()
    
    return render_template('index.html',
                         title='Inicio',
                         propiedades=propiedades,
                         inquilinos=inquilinos,
                         contratos_activos=contratos_activos)
