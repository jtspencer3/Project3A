"""Form class declaration."""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from datetime import date
from wtforms.fields.html5 import DateField
from wtforms.validators import URL, DataRequired, Email, EqualTo, Length
import csv


class StockForm(FlaskForm):
    with open('symbols.csv') as f:
        tuple_list = [tuple(line) for line in csv.reader(f)]
    symbol = SelectField("Choose Stock Symbol", [DataRequired()],
                         choices=tuple_list)
    chart_type = SelectField("Select Chart Type",[DataRequired()],
                             choices=[
                                 ("1", "1. Bar"), ("2", "2. Line"),
                              ],
                             )
    time_series = SelectField("Select Time Series",[DataRequired()],
                              choices=[
                                  ("1", "1. Intraday"),
                                  ("2", "2. Daily"),
                                  ("3", "3. Weekly"),
                                  ("4", "4. Monthly"),
                              ],
                              )

    start_date = DateField("Enter Start Date")
    end_date = DateField("Enter End Date")
    submit = SubmitField("Submit")



