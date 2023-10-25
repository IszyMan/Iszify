from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from forms import *
from models import *
from extensions import db
from flask_login import login_user, login_required, current_user
from utils import get_platform

user_blp = Blueprint("user_blp", __name__)


@user_blp.route('/', methods=["GET", "POST"])
def home():
    # form = GenerateBrandName()
    # posts = CreateProfile.query.all()
    if current_user.is_authenticated:
        return redirect(url_for('user_blp.admin'))
    if request.method == "POST" and "bt1" in request.form:
        original_url = request.form.get('url')
        short_url = generate_short_url()

        url = Urlshort(
            url=original_url,
            short_url=short_url,
        )
        url.save()
        # flash('URL has been shortened successfully!', 'success')
        return render_template("index.html",
                               shortened_url=f"{request.host_url}{short_url}",
                               original_url=original_url, show=1
                               )
    elif request.method == "POST" and "bt2" in request.form:
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
    return render_template("index.html")


@user_blp.route('/user/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    user_id = current_user.id
    brand_url = f"{request.host_url}{current_user.brand_name}"
    posts = CreateProfile.query.filter_by(author_id=user_id).all()

    url_short = Urlshort.query.filter_by(author_id=user_id).all()

    qr_codes_ = QrCode.query.filter_by(author_id=user_id).all()

    host_url = request.host_url
    brandie = current_user.brand_name
    return render_template("dashboard.html",
                           all_posts=posts, brand_url=brand_url,
                           brandie=brandie, host_url=host_url,
                           url_short=url_short, qr_codes_=qr_codes_)


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


# update brandname to user model
@user_blp.route('/update/brandname', methods=["POST"])
@login_required
def update_brandname():
    brandname = request.form.get('brandname')
    if not brandname:
        flash('Input Required', 'danger')
        return redirect(url_for('user_blp.dashboard'))
    user_ = User.query.filter_by(brand_name=brandname.lower()).first()
    if user_:
        # User with that brand already exists
        flash("Brand Name already exists!", "danger")
        return redirect(url_for('user_blp.dashboard'))
    current_user.brand_name = brandname.lower()
    db.session.commit()
    flash('Brand Name updated successfully!', 'success')
    return redirect(url_for('user_blp.admin'))


@user_blp.route('/delete/<linkname>')
@login_required
def delete_product(linkname):
    check_product = CreateProfile.query.filter_by(linkname=linkname.lower()).first()
    referer = request.headers.get('Referer')
    if not check_product:
        return render_template("404.html")
    db.session.delete(check_product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(referer or url_for('user_blp.dashboard'))


# SHORTEN URL SECTION
@user_blp.route('/urls/shorten_url', methods=['GET', 'POST'])
@login_required
def shorten_url():
    if request.method == 'POST':
        original_url = request.form.get('originalUrl')
        custom_url = request.form.get('customUrl', None)
        tracking_id = generate_tracking_id()
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

        short_url = f"{short_url}/scan?tracking_id={tracking_id}"

        url = Urlshort(
            author=current_user,
            author_id=current_user.id,
            url=original_url,
            tracking_id=tracking_id,
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
    if short_url == 'qr-code':
        return redirect(url_for('user_blp.qr_code_info'))
    if short_url == 'url-shortener':
        return redirect(url_for('user_blp.url_shortener_info'))
    if short_url == 'biolink':
        return redirect(url_for('user_blp.biolink'))
    url = Urlshort.query.filter_by(short_url=short_url).first_or_404()
    url.clicks += 1
    db.session.commit()
    print(url.url)
    return redirect(url.url)


# display all shortened urls with their original urls and clicks
@user_blp.route('/stats/urls', methods=['GET'])
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
    referer = request.headers.get('Referer')
    db.session.delete(url)
    db.session.commit()
    flash('URL deleted', 'success')
    return redirect(referer or url_for('user_blp.display_urls'))


# This is the page to display all the qr codes for the current user
@user_blp.route('/qr_codes', methods=['GET', 'POST'])
@login_required
def qr_codes():
    if request.method == 'POST':
        url = request.form.get('url')
        tracking_id = generate_tracking_id()
        if not url:
            flash('Please enter a URL', 'danger')
            return render_template("qr_codes.html")
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url

        url = url + f"/scan?tracking_id={tracking_id}"
        print(url, "this is the url")
        print(tracking_id, "this is the tracking id")
        # check if the url exists
        existing_qr_code = QrCode.query.filter_by(
            author_id=current_user.id,
            tracking_id=tracking_id,
            url=url).first()
        if existing_qr_code:
            flash('QR Code already exists', 'danger')
            return render_template("qr_codes.html", n=1, url=existing_qr_code.url)
        new_qr_code = QrCode(
            author=current_user,
            author_id=current_user.id,
            url=url
        )
        new_qr_code.save()
        flash('QR Code has been generated successfully!', 'success')
        return redirect(url_for('user_blp.display_qr_codes'))
    return render_template("qr_codes.html", n=0)


@user_blp.route('/scan', methods=['GET'])
def scan():
    tracking_id = request.args.get('tracking_id')
    user_agent = request.headers.get('User-Agent')
    ip_address = request.remote_addr

    # Create a new entry in the database
    scan_data = ScanData(tracking_id=tracking_id, ip_address=ip_address, user_agent=user_agent)
    db.session.add(scan_data)
    db.session.commit()

    return jsonify({'message': 'Data captured and stored in the database'})


# display all qr codes for the current user
@user_blp.route('/stats/qr_codes', methods=['GET'])
@login_required
def display_qr_codes():
    qrcodes = QrCode.query.filter_by(author_id=current_user.id).all()
    return render_template("display_qr.html", urls=qrcodes)


# delete a qr code
@user_blp.route('/qr_codes/delete/<int:qr_id>')
@login_required
def delete_qr_code(qr_id):
    # check if the qr code exists and if its for the current user
    qrcode = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).first_or_404()
    referer = request.headers.get('Referer')
    qrcode.delete()
    flash('QR Code deleted', 'success')
    return redirect(referer or url_for('user_blp.display_qr_codes'))


# qr code for all users (logged in or not )
@user_blp.route('/qr-code')
def qr_code_info():
    return render_template("qr_code_info.html")


@user_blp.route('/biolink')
def biolink():
    return render_template("biolink.html")


@user_blp.route('/url-shortener')
def url_shortener_info():
    return render_template("url_shortener_info.html")


@user_blp.route('/profile/<username>')
@login_required
def profile_info(username):
    return render_template("profile_info.html")


# list all bio links
@user_blp.route('/biolinks', methods=['GET'])
@login_required
def display_biolinks():
    biolinks = CreateProfile.query.filter_by(author_id=current_user.id).all()
    return render_template("biolinks.html", biolinks=biolinks)


@user_blp.route('/see', methods=['GET'])
def see():
    return render_template('base2.html')
