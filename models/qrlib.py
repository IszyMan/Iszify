from flask_login import UserMixin
from extensions import db
import datetime
from sqlalchemy import extract
from sqlalchemy.orm import relationship


class QrcodeRecord(UserMixin, db.Model):
    __tablename__ = "qr_code_record"
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.Integer, db.ForeignKey("qr_code.id"))
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    clicks = db.Column(db.Integer, default=0)


def save_qrcode_clicks(url_id):
    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = QrcodeRecord.query.filter(
        QrcodeRecord.qr_code_id == url_id,
        extract('year', QrcodeRecord.date) == current_year,
        extract('month', QrcodeRecord.date) == current_month,
        extract('day', QrcodeRecord.date) == current_day
    ).first()

    if not clicks:
        print("save new click record")
        new_record = QrcodeRecord(clicks=1, qr_code_id=url_id)
        db.session.add(new_record)
    else:
        print("update click record")
        clicks.clicks += 1

    db.session.commit()
    return True
