from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.models import Propietario

class PropietarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
    ])
    dni = StringField('DNI', validators=[
        DataRequired(message='El DNI es requerido'),
        Length(min=7, max=20, message='El DNI debe tener entre 7 y 20 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='El email no es válido'),
        Length(max=120, message='El email no puede tener más de 120 caracteres')
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es requerido'),
        Length(min=8, max=20, message='El teléfono debe tener entre 8 y 20 caracteres')
    ])

    def validate_dni(self, field):
        if self.dni.data:
            propietario = Propietario.query.filter_by(dni=field.data).first()
            if propietario and (not hasattr(self, 'id') or propietario.id != self.id):
                raise ValidationError('Este DNI ya está registrado.')

    def validate_email(self, field):
        if self.email.data:
            propietario = Propietario.query.filter_by(email=field.data).first()
            if propietario and (not hasattr(self, 'id') or propietario.id != self.id):
                raise ValidationError('Este email ya está registrado.')
