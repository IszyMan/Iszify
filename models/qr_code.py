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

    # add scan and tracking id to the url before saving to the database
    def add_tracking_id(self, url):
        self.url = url + f"/scan?tracking_id={self.tracking_id}"
        self.save()


class ScanData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), db.ForeignKey("qr_code.tracking_id"))
    ip_address = db.Column(db.String(20))
    user_agent = db.Column(db.String(200))

    def __repr__(self):
        return f"ScanData('{self.tracking_id}', '{self.ip_address}', '{self.user_agent}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_tracking_id(cls, tracking_id):
        return cls.query.filter_by(tracking_id=tracking_id).all()
