from flask_login import UserMixin
from extensions import db
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import extract, func


class CreateBioPage(UserMixin, db.Model):
    __tablename__ = "bio_page"
    id = db.Column(db.Integer, primary_key=True)
    # bio_page_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    bio_name = db.Column(db.String(250), default="")
    clicks = db.Column(db.Integer, default=0)
    links = relationship("CreateBioLinkEntries", backref="entries")


# clicks record model
class BioPageClicks(db.Model):
    __tablename__ = "bio_page_clicks"
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)
    bio_page_id = db.Column(db.Integer, db.ForeignKey("bio_page.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"Clicks('{self.bio_page_id}', '{self.created}')"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def save_commit(self):
        db.session.commit()


class BioPageClickLocation(db.Model):
    __tablename__ = "bio_page_click_location"
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(250))
    country = db.Column(db.String(250))
    city = db.Column(db.String(250))
    device = db.Column(db.String(250))
    browser = db.Column(db.String(250))
    bio_page_id = db.Column(db.Integer, db.ForeignKey("bio_page.id"))
    created = db.Column(db.DateTime, nullable=False, default=db.func.now())


def save_bio_page_clicks(url_id, payload):
    # Get today's date components
    today = datetime.datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # Query to find today's clicks for the given url_id
    clicks = BioPageClicks.query.filter(
        BioPageClicks.bio_page_id == url_id,
        extract("year", BioPageClicks.created) == current_year,
        extract("month", BioPageClicks.created) == current_month,
        extract("day", BioPageClicks.created) == current_day,
    ).first()

    if not clicks:
        print("save new click record")
        new_record = BioPageClicks(count=1, bio_page_id=url_id)
        db.session.add(new_record)
    else:
        print("update click record")
        clicks.count += 1

    db.session.commit()
    save_bio_page_click_location(
        payload["ip_address"],
        payload["country"],
        payload["city"],
        payload["device"],
        payload["browser_name"],
        url_id,
    )
    return True


# get bio page id
def get_bio_page_id(bio_name):
    bio_page = CreateBioPage.query.filter(
        func.lower(CreateBioPage.bio_name) == bio_name.lower()
    ).first()
    return bio_page.id


# update bio_page clicks
def update_bio_page_clicks(url_id):
    bio_page = CreateBioPage.query.get(url_id)
    bio_page.clicks += 1
    db.session.commit()
    return True


def save_bio_page_click_location(ip_address, country, city, device, browser, url_id):
    new_record = BioPageClickLocation(
        ip_address=ip_address,
        country=country,
        city=city,
        device=device,
        browser=browser,
        bio_page_id=url_id,
    )
    db.session.add(new_record)
    db.session.commit()

    return True
