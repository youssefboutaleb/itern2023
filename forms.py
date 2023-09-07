from wtforms import Form, StringField, DecimalField, IntegerField, TextAreaField, PasswordField, validators, DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed

#form used on Register page
class RegisterForm(Form):
    name = StringField('Full Name', [validators.Length(min=1,max=50)])
    username = StringField('Username', [validators.Length(min=4,max=25)])
    email = StringField('Email', [validators.Length(min=6,max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

#form used on the Transactions page
class ProfilForm(Form):
    start = DateField('Start Date', format='%Y-%m-%d', validators=[validators.DataRequired()])
    end = DateField('End Date', format='%Y-%m-%d', validators=[validators.DataRequired()])

#form used on the Buy page
class TransactForm(Form):
    amount = StringField('consumption', [validators.Length(min=1,max=50)])
class MultiTransactForm(Form):
    times = StringField('Timestamps (comma-separated)', [validators.Length(min=1, max=200)])
    amounts = StringField('Amounts (comma-separated)', [validators.Length(min=1, max=200)])
class TransactcsvForm(Form):
    csv_file = FileField('CSV File', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
