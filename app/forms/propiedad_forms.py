from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class PropiedadForm(FlaskForm):
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=200)])
    tipo = SelectField('Tipo', choices=[
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('local', 'Local Comercial'),
        ('oficina', 'Oficina'),
        ('otro', 'Otro')
    ])
    descripcion = TextAreaField('Descripción')
    propietario_id = SelectField('Propietario', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')
