from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Optional
from datetime import datetime, date

class FacturaForm(FlaskForm):
    fecha_emision = DateField('Fecha de Emisión', validators=[DataRequired()], format='%Y-%m-%d')
    monto = FloatField('Monto', validators=[DataRequired()])
    contrato_id = SelectField('Contrato', coerce=int, validators=[DataRequired()])
    pagado = BooleanField('Pagada')
    fecha_pago = DateField('Fecha de Pago', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Guardar')
    
    def validate_monto(self, field):
        if field.data <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
    
    def validate_fecha_emision(self, field):
        if field.data and isinstance(field.data, date) and field.data > date.today():
            raise ValidationError('La fecha de emisión no puede ser futura.')
            
    def validate_fecha_pago(self, field):
        if self.pagado.data and not field.data:
            raise ValidationError('Si la factura está pagada, debe especificar la fecha de pago.')
        if field.data and isinstance(field.data, date) and self.fecha_emision.data and isinstance(self.fecha_emision.data, date):
            if field.data < self.fecha_emision.data:
                raise ValidationError('La fecha de pago no puede ser anterior a la fecha de emisión.')
