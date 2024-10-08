from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from func import hex_id


class CreateBioLinkEntries(UserMixin, db.Model):
    __tablename__ = "bio_links_entries"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    author_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    bio_page_id = db.Column(db.String(50), db.ForeignKey("bio_page.id"))
    link_name = db.Column(db.String(250), nullable=False)
    link_url = db.Column(db.String(250), default="")
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
