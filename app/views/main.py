from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Propiedad, Inquilino, Contrato, Factura
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    # Contadores para las tarjetas
    propiedades = Propiedad.query.count()
    inquilinos = Inquilino.query.count()
    contratos_activos = Contrato.query.filter_by(activo=True).count()
    facturas_pendientes = Factura.query.filter_by(pagado=False).count()
    
    # Últimos contratos
    ultimos_contratos = Contrato.query.order_by(desc(Contrato.fecha_inicio)).limit(5).all()
    
    # Últimas facturas
    ultimas_facturas = Factura.query.order_by(desc(Factura.fecha_emision)).limit(5).all()
    
    return render_template('index.html',
                         title='Inicio',
                         propiedades=propiedades,
                         inquilinos=inquilinos,
                         contratos_activos=contratos_activos,
                         facturas_pendientes=facturas_pendientes,
                         ultimos_contratos=ultimos_contratos,
                         ultimas_facturas=ultimas_facturas)
