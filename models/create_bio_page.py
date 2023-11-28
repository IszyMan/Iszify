from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship


class CreateBioPage(UserMixin, db.Model):
    __tablename__ = "bio_page"
    id = db.Column(db.Integer, primary_key=True)
    # bio_page_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    bio_name = db.Column(db.String(250), default="")
    clicks = db.Column(db.Integer, default=0)
    links = relationship("CreateBioLinkEntries", backref="entries")
