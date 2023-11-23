from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class QrcodeRecord(UserMixin, db.Model):
    __tablename__ = "qr_code_record"
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey("qr_code.id"))
    date = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
