from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brand_name.brandname"))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    brand = relationship("ChooseBrandName", back_populates="brand")
    posts = relationship("CreateProfile", back_populates="author")
