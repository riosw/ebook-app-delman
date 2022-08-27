from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from . import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
ma = Marshmallow()
migrate = Migrate()

def create_app():
    app = Flask('ebook-app')

    # Configs
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inits
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    migrate.init_app(db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)

    return app