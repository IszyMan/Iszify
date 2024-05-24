from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_qrcode import QRcode


qr_code = QRcode()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
