from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import *
from models import *
from extensions import db
from flask_login import login_user, login_required, current_user
from utils import check_if_amazon_url_is_valid, check_if_youtube_url_is_valid, \
    check_if_twitter_url_is_valid, check_if_facebook_url_is_valid

user_blp = Blueprint("user_blp", __name__)


@user_blp.route('/', methods=["GET", "POST"])
def home():
    form = GenerateBrandName()
    # posts = CreateProfile.query.all()
    if request.method == "POST":
        brand_name = request.form.get('brandname').lower()
        if not brand_name:
            flash('Input Required', 'danger')
            return redirect(url_for('user_blp.home'))
        user_ = User.query.filter_by(brand_name=brand_name).first()
        if user_:
            # User with that brand already exists
            flash("Brand Name already exists!", "danger")
            return redirect(url_for('user_blp.home'))
        return redirect(url_for('auth_blp.register', brandie=brand_name))
    return render_template("index.html", form=form)


@user_blp.route('/join', methods=["GET", "POST"])
def join():
    # Every render_template has a logged_in variable set.
    form = GenerateBrandName()
    if request.method == "POST":
        brand_name = request.form.get('brandname')
        user_ = User.query.filter_by(brand_name=brand_name).first()
        if user_:
            # User already exists
            flash("Brand Name already exists!")
            return redirect(url_for('home'))

        new_user = User(brand_name=brand_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("auth_blp.register"))
    return render_template("join.html", form=form, current_user=current_user)


@user_blp.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    form = CreatePostForm()
    brand_url = f"{request.host_url}{current_user.brand_name}"
    posts = CreateProfile.query.all()
    if request.method == "POST":
        linkname = form.linkname.data
        twitter_link = form.twitter_link.data
        amazon_link = form.amazon_link.data
        youtube_link = form.youtube_link.data
        facebook_link = form.facebook_link.data
        product_ = form.product.data

        if twitter_link:
            if not check_if_twitter_url_is_valid(twitter_link):
                flash("Invalid Twitter URL", "danger")
                return redirect(url_for("user_blp.admin"))
        if amazon_link:
            if not check_if_amazon_url_is_valid(amazon_link):
                flash("Invalid Amazon URL", "danger")
                return redirect(url_for("user_blp.admin"))
        if youtube_link:
            if not check_if_youtube_url_is_valid(youtube_link) :
                flash("Invalid Youtube URL", "danger")
                return redirect(url_for("user_blp.admin"))
        if facebook_link:
            if not check_if_facebook_url_is_valid(facebook_link) :
                flash("Invalid Facebook URL", "danger")
                return redirect(url_for("user_blp.admin"))

        new_post = CreateProfile(
            linkname=linkname,
            twitter_link=twitter_link,
            amazon_link=amazon_link,
            youtube_link=youtube_link,
            facebook_link=facebook_link,
            product=product_,
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("user_blp.brand", brandname=current_user.brand_name))
    return render_template("admin.html", all_posts=posts,
                           name=current_user.first_name.title(),
                           logged_in=True,
                           form=form,
                           brand_url=brand_url)


@user_blp.route('/<path:sub_path>', methods=["GET", "POST"])
def profile(sub_path):
    requested_profile = ''
    all_profiles = User.query.all()
    for profiles in all_profiles:
        if profiles.first_name == sub_path:
            requested_profile = profiles
    return render_template("profile.html", all_posts=requested_profile, current_user=current_user)


# @user_blp.route('/', subdomain="<brandie>")
# def brand(brandie):
#     check_brand = User.query.filter_by(brand_name=brandie.lower()).first()
#     if not check_brand:
#         return render_template("404.html")
#     return render_template("brand.html", brandie=brandie.upper())

@user_blp.route('/<brandname>/', methods=["GET", "POST"])
def brand(brandname):
    check_brand = User.query.filter_by(brand_name=brandname.lower()).first()
    if not check_brand:
        return render_template("404.html")
    check_brand_posts = CreateProfile.query.filter_by(author_id=check_brand.id).all()
    return render_template("brand.html", brandie=brandname.upper(), all_posts=check_brand_posts[::-1])


@user_blp.route('/<brandname>/<linkname>', methods=["GET", "POST"])
def product(brandname, linkname):
    check_brand = User.query.filter_by(brand_name=brandname.lower()).first()
    if not check_brand:
        return render_template("404.html")
    check_product = CreateProfile.query.filter_by(linkname=linkname.lower()).first()
    if not check_product:
        return render_template("404.html")
    return render_template("product.html", brandie=brandname.upper(), linkname=linkname.upper(),
                           check_product=check_product)
