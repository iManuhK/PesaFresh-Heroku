from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import  current_user, login_required
from extensions import db, bcrypt
from models import User, Transaction
from transactions.forms import (WithdrawForm, ProductionForm, BorrowForm  )

transactions = Blueprint('transactions', __name__)

@transactions.route("/withdraw", methods=['GET', 'POST'])
@login_required
def withdraw():
    form = WithdrawForm()
    if form.validate_on_submit():
        withdraw_amount = form.withdraw_amount.data

        # Check if the withdrawal amount exceeds the wallet balance
        if withdraw_amount > current_user.wallet_balance:
            flash(f"Insufficient funds! You only have Ksh. {current_user.wallet_balance} in your wallet.", 'danger')
            return redirect(url_for('transactions.withdraw'))

        # Create a new transaction for the withdrawal
        transaction = Transaction(
            user_id=current_user.id, 
            transaction_type='withdrawal',
            description=form.description.data, 
            withdraw_amount=withdraw_amount
        )
        
        # Update the wallet balance after the withdrawal
        current_user.wallet_balance -= withdraw_amount

        # save to the db
        db.session.add(transaction)
        db.session.commit()

        flash('Withdrawal successful!', 'success')
        return redirect(url_for('transactions.withdraw'))

    return render_template('withdraw.html', title='Withdraw', form=form)


@transactions.route("/production", methods=['GET', 'POST'])
@login_required
def production():
    form = ProductionForm()
    if form.validate_on_submit():
        transaction = Transaction(user_id=current_user.id, 
                                 transaction_type=form.transaction_type.data, 
                                 description=form.description.data, 
                                 product=form.product.data,
                                 kgs=form.kgs.data,
                                 cost_per_kg = form.cost_per_kg.data)
        
        # Calculate total produced using the Transaction model's method
        transaction.total_amount = transaction.calculate_amount_from_product()
        
        db.session.add(transaction)
        db.session.commit()
        
        # Update the user's credit limit
        current_user.update_credit_limit()

        flash('Production successful!', 'success')
        return redirect(url_for('transactions.production'))
    return render_template('production.html', title='Production', form=form)

@transactions.route("/borrow", methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    if form.validate_on_submit():
        borrow_amount = form.borrowed_amount.data

        try:
            # Create a new transaction instance
            transaction = Transaction(
                user_id=current_user.id,
                description=form.description.data,
                borrowed_amount=borrow_amount
            )
            
            # Process borrowing and ensure it checks the credit limit and wallet balance
            transaction.process_borrowing(user=current_user, borrow_amount=borrow_amount)

            # Add the transaction to the session and commit
            db.session.add(transaction)
            db.session.commit()

            # Provide feedback to the user
            flash(f'Borrow successful! Ksh. {borrow_amount} has been added to your wallet.', 'success')
            return redirect(url_for('transactions.borrow'))

        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('borrow.html', title='Borrow', form=form)

@transactions.route("/transactions")
@login_required
def transactions_history():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', transactions=transactions)

@transactions.route("/transaction/<int:transaction_id>")
@login_required
def transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('transaction.html', transaction=transaction)


