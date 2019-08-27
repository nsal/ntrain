from flask_wtf import FlaskForm
from wtforms import  BooleanField, TextField, SelectField #, StringField, PasswordField, SubmitField, 
from wtforms.validators import DataRequired

class MainForm(FlaskForm):
    choices = [('smd', 'same day return'), 
               ('ow', 'one way')]
    # username = StringField('Username', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])
    # choices = [('BFD', 'Brentford'), ('SAL', 'Salisbury')]
    # origin = SelectField(u'Programming Language', choices=choices)
    same_day_return = BooleanField('Same day return')
    weekends_only = BooleanField('Weekends only')
    # submit = SubmitField('Sign in')
    origin = TextField('Where from', id='origin_station_autocomplete', validators=[DataRequired()])
    destination = TextField('Where to', id='destination_station_autocomplete', validators=[DataRequired()])
    return_options = SelectField('Return', choices=choices)

