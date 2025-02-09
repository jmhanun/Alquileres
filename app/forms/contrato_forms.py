from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, FloatField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime

class ContratoForm(FlaskForm):
    propiedad_id = SelectField('Propiedad', coerce=int, validators=[DataRequired()])
    inquilino_id = SelectField('Inquilino', coerce=int, validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de Fin', validators=[DataRequired()])
    monto_mensual = FloatField('Monto Mensual ($)', validators=[DataRequired()])
    deposito = FloatField('Depósito ($)')
    notas = TextAreaField('Notas')
    submit = SubmitField('Guardar')
    
    def validate_fecha_fin(self, field):
        if field.data <= self.fecha_inicio.data:
            raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
        
    def validate_monto_mensual(self, field):
        if field.data <= 0:
            raise ValidationError('El monto mensual debe ser mayor a 0.')
            
    def validate_deposito(self, field):
        if field.data and field.data < 0:
            raise ValidationError('El depósito no puede ser negativo.')
