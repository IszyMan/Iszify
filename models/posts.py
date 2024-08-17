from extensions import db
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy import extract, func
from func import hex_id


class Categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    name = db.Column(db.String(250), nullable=False)
    posts = relationship("Posts", backref="category")


class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.String(50), primary_key=True, default=hex_id)
    post_title = db.Column(db.String(250), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    category_id = db.Column(db.String(50), db.ForeignKey("categories.id"))


def save_create_post(title, content, category_id):
    post = Posts(
        post_title=title,
        post_content=content,
        category_id=category_id
    )

    db.session.add(post)
    db.session.commit()

    return True


def get_posts(page, per_page, category_id=None):
    query = Posts.query.order_by(Posts.created_at.desc())

    if category_id:
        query = query.filter_by(category_id=category_id)

    # Apply pagination to the query
    paginated_posts = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_posts


def get_one_post(post_id):
    return Posts.query.filter_by(id=post_id).first()


def get_categories():
    categories = Categories.query.all()
    return categories


# categ = ["QR code", "Link-in-bio", "URL shorter"]
#
# def create_categories():
#     for i in categ:
#         print(i)
#         category = Categories(name=i)
#         db.session.add(category)
#         db.session.commit()
#
#     return True
