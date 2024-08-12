from flask_login import UserMixin
from extensions import db
import datetime
from sqlalchemy import extract
from sqlalchemy.orm import relationship
from func import hex_id


class QrcodeRecord(UserMixin, db.Model):
    __tablename__ = "qr_code_record"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    qr_code_id = db.Column(db.String(50), db.ForeignKey("qr_code.id"))
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    clicks = db.Column(db.Integer, default=0)


class QrCodeClickLocation(UserMixin, db.Model):
    __tablename__ = "qr_code_click_location"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    ip_address = db.Column(db.String(250))
    country = db.Column(db.String(250))
    city = db.Column(db.String(250))
    device = db.Column(db.String(250))
    browser = db.Column(db.String(250))
    qr_code_id = db.Column(db.String(50), db.ForeignKey("qr_code.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())


def save_qrcode_clicks(url_id, payload):
    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = QrcodeRecord.query.filter(
        QrcodeRecord.qr_code_id == url_id,
        extract("year", QrcodeRecord.date) == current_year,
        extract("month", QrcodeRecord.date) == current_month,
        extract("day", QrcodeRecord.date) == current_day,
    ).first()

    if not clicks:
        print("save new click record")
        new_record = QrcodeRecord(clicks=1, qr_code_id=url_id)
        db.session.add(new_record)
    else:
        print("update click record")
        clicks.clicks += 1

    db.session.commit()
    save_qrcode_click_location(
        payload["ip_address"],
        payload["country"],
        payload["city"],
        payload["device"],
        payload["browser_name"],
        url_id,
    )
    return True


def save_qrcode_click_location(ip_address, country, city, device, browser, url_id):
    new_record = QrCodeClickLocation(
        ip_address=ip_address,
        country=country,
        city=city,
        device=device,
        browser=browser,
        qr_code_id=url_id,
    )
    db.session.add(new_record)
    db.session.commit()
    return True
