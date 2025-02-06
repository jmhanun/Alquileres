from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.models import Inquilino

class InquilinoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    dni = StringField('DNI', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    submit = SubmitField('Guardar')
    
    def validate_dni(self, field):
        inquilino = Inquilino.query.filter_by(dni=field.data).first()
        if inquilino and inquilino.id != getattr(self, '_inquilino_id', None):
            raise ValidationError('Este DNI ya está registrado.')
    
    def validate_email(self, field):
        inquilino = Inquilino.query.filter_by(email=field.data).first()
        if inquilino and inquilino.id != getattr(self, '_inquilino_id', None):
            raise ValidationError('Este email ya está registrado.')
