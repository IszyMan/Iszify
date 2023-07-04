from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
