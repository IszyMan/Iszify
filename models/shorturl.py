from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from hashids import Hashids
# from main import create_app
from urllib import request
from urllib.error import HTTPError, URLError
from secrets import token_hex


def generate_tracking_id():
    return token_hex(16)


secret = 'any-secret-key-you-choose'
print("secret")
print(secret)

hashids = Hashids(min_length=6, salt=secret)


# url shortener table
class Urlshort(UserMixin, db.Model):
    __tablename__ = "url_shortener"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    author = relationship("User", back_populates="urlshort")
    url = db.Column(db.String(250))
    tracking_id = db.Column(db.String(250), nullable=True)
    short_url = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Urlshort('{self.url}', '{self.short_url}', '{self.clicks}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()


# generate short url
def generate_short_url():
    last_url = Urlshort.query.order_by(Urlshort.id.desc()).first()

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
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    try:
        request.urlopen(url)
        return True
    except (HTTPError, URLError):
        return False


class ShortUrlSacnData(db.Model):
    __tablename__ = "short_url_scan_data"
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(50), db.ForeignKey("url_shortener.tracking_id"))
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

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    