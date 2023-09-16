from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import *
from models import *
from extensions import db
from flask_login import login_user, login_required, current_user
from utils import get_platform

user_blp = Blueprint("user_blp", __name__)


@user_blp.route('/', methods=["GET", "POST"])
def home():
    form = GenerateBrandName()
    # posts = CreateProfile.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('user_blp.admin'))
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


@user_blp.route('/user/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = current_user.id
    brand_url = f"{request.host_url}{current_user.brand_name}"
    posts = CreateProfile.query.filter_by(author_id=user_id).all()

    url_short = Urlshort.query.filter_by(author_id=user_id).all()

    host_url = request.host_url
    brandie = current_user.brand_name
    return render_template("dashboard.html",
                           all_posts=posts, brand_url=brand_url,
                           brandie=brandie, host_url=host_url,
                           url_short=url_short,)


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


@user_blp.route('/redirect')
@login_required
def redirect_me():
    return render_template("redirect.html")


@user_blp.route('/user/admin', methods=["GET", "POST"])
@login_required
def admin():
    form = CreatePostForm()
    user_id = current_user.id
    brand_url = f"{request.host_url}brand/{current_user.brand_name}"
    posts = CreateProfile.query.filter_by(author_id=user_id).all()
    brandname = current_user.brand_name
    if request.method == "POST":
        linkname = form.linkname.data.lower()
        link = form.link.data.lower()

        # if not linkname:
        #     flash("Link Name Required", "danger")
        #     return redirect(url_for("user_blp.admin"))

        check_if_linkname_exists = CreateProfile.query.filter_by(linkname=linkname).first()
        if check_if_linkname_exists:
            flash("Link Name already exists!", "danger")
            return redirect(url_for("user_blp.admin"))

        new_post = CreateProfile(
            linkname=linkname,
            link=link,
            link_name=get_platform(link),
            author=current_user,
            author_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Link Added", "success")
        return redirect(url_for("user_blp.admin"))
    return render_template("admin.html", all_posts=posts,
                           name=current_user.first_name.title(),
                           logged_in=True,
                           form=form,
                           brand_url=brand_url,
                           brandie=brandname,
                           host_url=request.host_url)


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

@user_blp.route('/brand/<brandname>/', methods=["GET", "POST"])
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
    check_product.clicks += 1
    db.session.commit()
    return render_template("product.html", brandie=brandname.upper(), linkname=linkname.upper(),
                           check_product=check_product)


@user_blp.route('/delete/<linkname>')
@login_required
def delete_product(linkname):
    check_product = CreateProfile.query.filter_by(linkname=linkname.lower()).first()
    if not check_product:
        return render_template("404.html")
    db.session.delete(check_product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('user_blp.dashboard'))


# SHORTEN URL SECTION
@user_blp.route('/urls/shorten_url', methods=['GET', 'POST'])
@login_required
def shorten_url():
    if request.method == 'POST':
        original_url = request.form.get('originalUrl')
        custom_url = request.form.get('customUrl', None)
        if Urlshort.query.filter_by(
                author_id=current_user.id,
                url=original_url).first():
            flash('URL already exists', 'danger')
            return render_template("shorten.html")
        # if not validate_url(original_url):
            # flash('Please enter a valid URL', 'danger')
            # return render_template("shorten.html")

        if custom_url:
            short_url = custom_url
            if Urlshort.query.filter_by(short_url=short_url).first():
                flash('Custom URL already exists', 'danger')
                return render_template("shorten.html")
        else:
            short_url = generate_short_url()
            print(generate_short_url())

        url = Urlshort(
            author=current_user,
            author_id=current_user.id,
            url=original_url,
            short_url=short_url,
        )
        url.save()
        flash('URL has been shortened successfully!', 'success')
        return render_template("shorten.html",
                               shortened_url=f"{request.host_url}{short_url}",
                               original_url=original_url
                               )

    return render_template("shorten.html")


# redirect short url to the original url
@user_blp.route('/<short_url>/')
def redirect_to_url(short_url):
    url = Urlshort.query.filter_by(short_url=short_url).first_or_404()
    url.clicks += 1
    db.session.commit()
    print(url.url)
    return redirect(url.url)


# display all shortened urls with their original urls and clicks
@user_blp.route('/stats/urls')
@login_required
def display_urls():
    urls = Urlshort.query.filter_by(author_id=current_user.id).all()
    return render_template("urls.html", urls=urls)


# delete a shortened url
@user_blp.route('/urls/delete/<int:url_id>')
@login_required
def delete_url(url_id):
    # check if the url exists and if its for the current user
    url = Urlshort.query.filter_by(id=url_id, author_id=current_user.id).first_or_404()
    db.session.delete(url)
    db.session.commit()
    flash('URL deleted', 'success')
    return redirect(url_for('user_blp.display_urls'))


# This is the page to display all the qr codes for the current user
@user_blp.route('/qr_codes', methods=['GET'])
@login_required
def qr_codes():
    # query for short urls for a current user
    urls = Urlshort.query.filter_by(author_id=current_user.id).all()
    return render_template("qr_codes.html", urls=urls)
