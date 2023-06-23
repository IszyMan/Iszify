from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class ChooseBrandName(UserMixin, db.Model):
    __tablename__ = "brand_name"
    id = db.Column(db.Integer, primary_key=True)
    brandname = db.Column(db.String(100), unique=True)
    brand = relationship("User", back_populates="brand")
