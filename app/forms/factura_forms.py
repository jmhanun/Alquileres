from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime

class FacturaForm(FlaskForm):
    fecha_emision = DateField('Fecha de Emisión', validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired()])
    contrato_id = SelectField('Contrato', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
    def validate_monto(self, field):
        if field.data <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
    
    def validate_fecha_emision(self, field):
        if field.data > datetime.now().date():
            raise ValidationError('La fecha de emisión no puede ser futura.')
