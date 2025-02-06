import os
from app import create_app, db
from app.models import User, Propietario, Propiedad, Inquilino, Contrato, Factura

app = create_app(os.getenv('FLASK_ENV', 'default'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Propietario': Propietario,
        'Propiedad': Propiedad,
        'Inquilino': Inquilino,
        'Contrato': Contrato,
        'Factura': Factura
    }

if __name__ == '__main__':
    app.run()
