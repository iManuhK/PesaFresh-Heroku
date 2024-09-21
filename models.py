from datetime import datetime
from extensions import db
from flask_login import UserMixin
from extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    national_id = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    transactions = db.relationship('Transaction', backref='creator', lazy=True)
    credit_limit = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=0)
    wallet_balance = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=0)


    def calculate_credit_limit(self):
        total_production = db.session.query(db.func.sum(Transaction.kgs)).filter(
            Transaction.user_id == self.id,
            Transaction.transaction_type == 'production'
        ).scalar() or 0
        return total_production * 5 

    def update_credit_limit(self):
        self.credit_limit = self.calculate_credit_limit()
        db.session.commit()

    def update_wallet_balance(self, amount):
        """
        Update the user's wallet balance by adding the given amount.
        """
        if self.wallet_balance is None:
            self.wallet_balance = 0
        self.wallet_balance += amount
        db.session.commit()

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    borrowed_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    withdraw_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    product = db.Column(db.String(20), nullable=True)
    kgs = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    cost_per_kg = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    total_amount = db.Column(db.Numeric(precision=10, scale=2), nullable=True)

    def calculate_amount_from_product(self):
        return self.kgs * self.cost_per_kg

    def validate_borrowed_amount(self):
        if self.borrowed_amount is None:
            raise ValueError('Borrowed amount is missing')
        if self.borrowed_amount > self.creator.credit_limit:
            raise ValueError('Borrowed amount exceeds credit limit')
        return self.borrowed_amount

    def calculate_wallet_balance(self):
        if self.creator.wallet_balance is None:
            self.creator.wallet_balance = 0
        return self.wallet_balance + (self.borrowed_amount or 0) - (self.withdraw_amount or 0)
    
    def process_borrowing(self, user, borrow_amount):
        """
        Process a borrowing transaction by checking if the borrow amount is within the user's credit limit,
        then updating both the wallet balance and the user's credit limit.
        """
        # Check if borrow amount exceeds the credit limit
        if borrow_amount > user.credit_limit:
            raise ValueError(f"Cannot borrow more than the credit limit! Your credit limit is Ksh. {user.credit_limit}")

        # Update user's wallet balance by adding the borrowed amount
        user.update_wallet_balance(borrow_amount)

        # Reduce the user's credit limit by the borrowed amount
        user.credit_limit -= borrow_amount

        # Set the transaction's borrowed amount (outstanding loan)
        self.borrowed_amount = borrow_amount
        self.transaction_type = 'borrow'
        db.session.commit()

