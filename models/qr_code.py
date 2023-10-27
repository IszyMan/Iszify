from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from secrets import token_hex


def generate_tracking_id():
    return token_hex(16)


# create qr code table
class QrCode(UserMixin, db.Model):
    __tablename__ = "qr_code"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    url = db.Column(db.Text)
    tracking_id = db.Column(db.String(250), nullable=True, default=generate_tracking_id())
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    author = relationship("User", back_populates="qr_code")

    def __repr__(self):
        return f"QrCode('{self.url}', '{self.created_at}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
