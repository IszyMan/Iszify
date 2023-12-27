from flask import Flask
from auth import auth_blp
from views.user_view import user_blp
from extensions import login_manager, db, bootstrap, migrate, qr_code
from models import User
import os


def create_app():
    app = Flask(__name__)

    base_dir = os.path.dirname(os.path.realpath(__file__))
    app.config["SECRET_KEY"] = "any-secret-key-you-choose"
    # The configuration for the URI of the database, the link2ru.db is the name of this project's dev database
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        base_dir, "link2ru.sqlite3"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SERVER_NAME"] = os.getenv("SERVER_NAME", "localhost:5000")

    login_manager.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    qr_code.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_blp)
    app.register_blueprint(user_blp)

    return app
