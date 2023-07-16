from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class CreateProfile(UserMixin, db.Model):
    __tablename__ = "users_links"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    product = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    linkname = db.Column(db.String(250), nullable=False)
    twitter_link = db.Column(db.String(250), default="")
    facebook_link = db.Column(db.String(250), default="")
    amazon_link = db.Column(db.String(250), default="")
    youtube_link = db.Column(db.String(250), default="")
