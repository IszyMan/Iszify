from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
from hashids import Hashids

# from main import create_app
from urllib import request
from urllib.error import HTTPError, URLError
import datetime

secret = "any-secret-key-you-choose"

hashids = Hashids(min_length=6, salt=secret)

default_title = f'untitled {datetime}'


# url shortener table
class Urlshort(UserMixin, db.Model):
    __tablename__ = "url_shortener"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    url = db.Column(db.String(250))
    short_url = db.Column(db.String(250))
    title = db.Column(db.String(250))
    clicks = db.Column(db.Integer, default=0)
    want_qr_code = db.Column(db.Boolean, default=False)
    qr_data = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Urlshort('{self.url}', '{self.short_url}', '{self.clicks}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()


# clicks model
class UrlShortenerClicks(db.Model):
    __tablename__ = "url_shortener_clicks"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)
    url_id = db.Column(db.Integer, db.ForeignKey("url_shortener.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.url_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def save_commit(self):
        db.session.commit()


def save_url_clicks(url_id):
    todays_date = datetime.datetime.now().strftime("%d-%b-%Y")

    clicks = UrlShortenerClicks.query.filter_by(
        url_id=url_id, created=todays_date
    ).first()
    if not clicks:
        print("save new click record")
        new_clicks = UrlShortenerClicks(count=1, url_id=url_id)
        new_clicks.save()
    else:
        print("update click record")
        clicks.count += 1
        clicks.save_commit()

    return True


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
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        request.urlopen(url)
        return True
    except (HTTPError, URLError):
        return False
