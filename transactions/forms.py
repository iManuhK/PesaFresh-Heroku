from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class WithdrawForm(FlaskForm):
    transaction_type = StringField('Transaction Type',
                        validators=[DataRequired()], default="withdrawal")
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=100)])
    withdraw_amount = DecimalField('Amount you wish to withdraw', 
                          validators=[DataRequired(), NumberRange(min=0, message="Amount must be positive.")])
    submit = SubmitField('Withdraw')

class ProductionForm(FlaskForm):
    transaction_type = StringField('Transaction Type',
                        validators=[DataRequired()], default="production")
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=100)])
    product = StringField('Product', validators=[DataRequired(), Length(min=2, max=100)])
    kgs = DecimalField('Unit Kgs', 
                       validators=[DataRequired(), NumberRange(min=0, message="Kgs must be positive.")])
    cost_per_kg = DecimalField('Cost per Kg', 
                               validators=[DataRequired(), NumberRange(min=0, message="Cost per kg must be positive.")])
    submit = SubmitField('Save')

class BorrowForm(FlaskForm):
    transaction_type = StringField('Transaction Type',
                        validators=[DataRequired()], default="borrowing")    
    description = StringField('Description', validators=[DataRequired(), Length(min=2, max=100)])
    borrowed_amount = DecimalField('Amount you want to Borrow', 
                                   validators=[DataRequired(), NumberRange(min=0, message="Borrowed amount must be positive.")])
    submit = SubmitField('Borrow')
