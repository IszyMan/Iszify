from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from hashids import Hashids
from urllib import request
from urllib.error import HTTPError, URLError
from func import hex_id
import hashlib, uuid
from sqlalchemy.dialects.postgresql import BYTEA

secret = "any-secret-key-you-choose"

hashids = Hashids(min_length=6, salt=secret)


# create qr code table
class QrCode(UserMixin, db.Model):
    __tablename__ = "qr_code"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    author_id = db.Column(db.String(50), db.ForeignKey("users.id"))
    title = db.Column(db.String(250))
    qr_data = db.Column(BYTEA)
    url = db.Column(db.Text)
    email = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    qrcode_record = relationship("QrcodeRecord", backref="qr_code")
    short_url = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
    # # vcard
    name = db.Column(db.String(250))
    org = db.Column(db.String(250))
    phone = db.Column(db.String(250))
    website = db.Column(db.Text)
    mail = db.Column(db.String(250))
    address = db.Column(db.Text)
    note = db.Column(db.Text)
    # # WIFI
    ssid = db.Column(db.String(250))
    password = db.Column(db.String(250))

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
    # Retrieve the last UUID (string) inserted in the database
    last_url = QrCode.query.order_by(QrCode.id.desc()).first()

    if not last_url:
        # If no URLs exist in the database, generate a new UUID-based ID
        new_uuid = uuid.uuid4().hex
    else:
        # Use the last UUID if it exists
        new_uuid = last_url.id

    # Hash the UUID to create a shorter URL
    short_hash = hashlib.sha256(new_uuid.encode()).hexdigest()[:8]  # Use the first 8 characters for brevity

    return f"Q{short_hash}"


# validate url
def validate_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        request.urlopen(url)
        return True
    except (HTTPError, URLError):
        return False


def create_qr_want(short_ur, url, title, current_user, res):
    new_qr_code = QrCode(
        author=current_user,
        author_id=current_user.id,
        url=url,
        qr_data=res,
        short_url=short_ur,
        title=title,
    )
    new_qr_code.save()

    return new_qr_code
