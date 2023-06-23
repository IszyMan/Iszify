from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class CreateProfile(UserMixin, db.Model):
    __tablename__ = "users_links"
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.Integer, db.ForeignKey("users.name"))
    author = relationship("User", back_populates="posts")
    linkname = db.Column(db.String(250), nullable=False)
    yourlink = db.Column(db.String(250), nullable=False)
