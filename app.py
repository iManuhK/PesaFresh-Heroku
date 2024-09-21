# app.py

from flask import Flask
from extensions import db, bcrypt, login_manager, migrate, mail
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Import and register Blueprints
    from users.routes import users
    from main.routes import main
    from transactions.routes import transactions
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(transactions)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5555, debug=True)
