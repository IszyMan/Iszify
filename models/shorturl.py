from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from hashids import Hashids

# from main import create_app
from urllib import request
from urllib.error import HTTPError, URLError
import datetime
from sqlalchemy import extract
from func import hex_id
import uuid, hashlib
from sqlalchemy.dialects.postgresql import BYTEA

secret = "any-secret-key-you-choose"

hashids = Hashids(min_length=6, salt=secret)

default_title = f"untitled {datetime}"


# url shortener table
class Urlshort(UserMixin, db.Model):
    __tablename__ = "url_shortener"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    author_id = db.Column(db.String(50), db.ForeignKey("users.id"), nullable=True)
    url = db.Column(db.String(250))
    short_url = db.Column(db.String(250))
    title = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
    want_qr_code = db.Column(db.Boolean, default=False)
    qr_data = db.Column(BYTEA)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Urlshort('{self.url}', '{self.short_url}', '{self.clicks}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()


# clicks model
class UrlShortenerClicks(db.Model):
    __tablename__ = "url_shortener_clicks"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    count = db.Column(db.Integer, default=0)
    url_id = db.Column(db.String(50), db.ForeignKey("url_shortener.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.url_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def save_commit(self):
        db.session.commit()


class ShortUrlClickLocation(db.Model):
    __tablename__ = "short_url_click_location"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    ip_address = db.Column(db.String(250))
    country = db.Column(db.String(250))
    city = db.Column(db.String(250))
    device = db.Column(db.String(250))
    browser = db.Column(db.String(250))
    url_id = db.Column(db.String(50), db.ForeignKey("url_shortener.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.url_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def save_commit(self):
        db.session.commit()


def save_url_clicks(url_id, payload):
    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = UrlShortenerClicks.query.filter(
        UrlShortenerClicks.url_id == url_id,
        extract("year", UrlShortenerClicks.created) == current_year,
        extract("month", UrlShortenerClicks.created) == current_month,
        extract("day", UrlShortenerClicks.created) == current_day,
    ).first()

    if not clicks:
        print("save new click record")
        new_clicks = UrlShortenerClicks(count=1, url_id=url_id)
        db.session.add(new_clicks)
    else:
        print("update click record")
        clicks.count += 1

    db.session.commit()
    save_url_click_location(
        payload["ip_address"],
        payload["country"],
        payload["city"],
        payload["device"],
        payload["browser_name"],
        url_id,
    )
    return True


# generate short url
def generate_short_url():
    last_url = Urlshort.query.order_by(Urlshort.id.desc()).first()

    if not last_url:
        # If no URLs exist in the database, initialize the counter to 1
        new_uuid = uuid.uuid4().hex
    else:
        # Use the last UUID if it exists
        new_uuid = last_url.id

    # Generate the short URL using the counter
    hashid = hashlib.sha256(new_uuid.encode()).hexdigest()[:8]
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


def save_url_click_location(ip_address, country, city, device, browser, url_id):
    new_record = ShortUrlClickLocation(
        ip_address=ip_address,
        country=country,
        city=city,
        device=device,
        browser=browser,
        url_id=url_id,
    )
    db.session.add(new_record)
    db.session.commit()
    return True
