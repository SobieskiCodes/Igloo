from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class FactionIDForm(FlaskForm):
    WarbaseFaction = StringField('FactionID', validators=[DataRequired(), Length(min=-1, max=20,
                                                                        message='You cant have more than 20 characters')])