# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class UserProfileForm(FlaskForm):
    bio = TextAreaField('Bio')
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Save')
