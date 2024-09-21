from flask import render_template, Blueprint, request
from models import Transaction

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('homepage.html', title = 'Home')

@main.route("/about")
def about():
    return render_template('about.html', title='About')
