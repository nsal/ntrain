from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired()])
    same_day_return = BooleanField('Same day return')
    weekends_only = BooleanField('Weekends only')
    # submit = SubmitField('Sign in')
