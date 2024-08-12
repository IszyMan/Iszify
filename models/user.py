from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from flask import request
from random import randint
from func import hex_id


def generate_otp():
    otp = randint(100000, 999999)
    return str(otp)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    otp = db.Column(db.String(100), default=generate_otp)
    profile_link = db.Column(db.String(250), unique=True)
    email_verified = db.Column(db.Boolean, default=False)
    brand_name = db.Column(db.String(100))
    bio_name = relationship("CreateBioPage", backref="author")
    posts = relationship("CreateProfile", backref="author")
    urlshort = relationship("Urlshort", backref="author")
    qr_code = relationship("QrCode", backref="author")
    link_entries = relationship("CreateBioLinkEntries", backref="author")


def get_profile_link(brand_name):
    return f"{request.host_url}{brand_name}"


# update otp
def update_otp(user):
    user.otp = generate_otp()
    db.session.commit()
    return user.otp
