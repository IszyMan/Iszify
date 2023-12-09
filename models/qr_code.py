from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from hashids import Hashids
from urllib import request
from urllib.error import HTTPError, URLError


secret = "any-secret-key-you-choose"

hashids = Hashids(min_length=6, salt=secret)


# create qr code table
class QrCode(UserMixin, db.Model):
    __tablename__ = "qr_code"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250))
    url = db.Column(db.Text)
    email = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    qrcode_record = relationship("QrcodeRecord", backref="qr_code")
    short_url = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
    # vcard
    name = db.Column(db.Text)
    org = db.Column(db.Text)
    phone = db.Column(db.Text)
    mail = db.Column(db.Text)
    website = db.Column(db.Text)
    address = db.Column(db.Text)
    note = db.Column(db.Text)




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


def generate_short_url2():
    last_url = QrCode.query.order_by(QrCode.id.desc()).first()

    if not last_url:
        # If no URLs exist in the database, initialize the counter to 1
        counter = 1
    else:
        last_id = last_url.id
        counter = last_id + 1

    # Generate the short URL using the counter
    hashid = hashids.encode(counter)
    return hashid


# validate url
def validate_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        request.urlopen(url)
        return True
    except (HTTPError, URLError):
        return False
