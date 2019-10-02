from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
import os

class ReportSelect(FlaskForm):
    Report = SelectField('Select Report', choices=list((x[:-5], x[:-5]) for x in os.listdir("./reports") if x.endswith('.json')))


class FactionIDForm(FlaskForm):
    WarbaseFaction = StringField('FactionID', validators=[DataRequired(), Length(min=-1, max=20,
                                                                        message='You cant have more than 20 characters')])