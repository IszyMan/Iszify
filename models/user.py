from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from flask import request


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # brand_id = db.Column(db.Integer, db.ForeignKey("brand_name.brandname")) # NOT IN USE
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True, nullable=False)
    brand_name = db.Column(db.String(100))
    profile_link = db.Column(db.String(250), unique=True)
    # brand = relationship("ChooseBrandName", back_populates="brand") #THIS IS NOT IN USE
    posts = relationship("CreateProfile", back_populates="author")
    urlshort = relationship("Urlshort", back_populates="author")


def get_profile_link(brand_name):
    return f"{request.host_url}{brand_name}"
