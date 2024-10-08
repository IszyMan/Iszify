import os
from flask import Flask, render_template
import base64
from auth import auth_blp
from extensions import login_manager, db, bootstrap, migrate, qr_code, mail, ckeditor
from models import User
from views.user_view import user_blp
from dotenv import load_dotenv
import traceback

load_dotenv()


def create_app():
    app = Flask(__name__)

    base_dir = os.path.dirname(os.path.realpath(__file__))
    app.config["SECRET_KEY"] = "any-secret-key-you-choose"
    # The configuration for the URI of the database, the link2ru.db is the name of this project's dev database
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    #     base_dir, "link2ru.sqlite3"
    # )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SERVER_NAME"] = os.getenv("SERVER_NAME", "localhost:5000")
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USERNAME"] = "easytransact.send@gmail.com"
    app.config["MAIL_PASSWORD"] = "xnueeryfwkbuqhou"
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True

    login_manager.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    qr_code.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    # 500 error handler
    @app.errorhandler(500)
    def internal_error(error):
        print(traceback.format_exc(), "error@500Traceback")
        print(error, "error@500")
        db.session.rollback()
        return render_template("500.html"), 500

    @app.template_filter("urlsafe")
    def urlsafe_filter(s):
        return (
            base64.b64encode(s)
            .decode("utf-8")
            .replace("+", "-")
            .replace("/", "_")
            .replace("=", "")
        )

    app.register_blueprint(auth_blp)
    app.register_blueprint(user_blp)

    return app
