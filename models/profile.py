from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from func import hex_id


class CreateProfile(UserMixin, db.Model):
    __tablename__ = "users_links"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    author_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    description = db.Column(db.Text, default="")
    linkname = db.Column(db.String(250), nullable=False)
    link = db.Column(db.String(250), default="")
    link_name = db.Column(db.String(250), default="")
    clicks = db.Column(db.Integer, default=0)
