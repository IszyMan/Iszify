from flask import Flask
from auth import auth_blp
from views.user_view import user_blp
from extensions import login_manager, db, bootstrap, migrate
from models import User


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    login_manager.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    migrate.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_blp)
    app.register_blueprint(user_blp)

    return app
