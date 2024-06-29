from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from forms import *
from models import *
from extensions import db
from flask_login import login_user, login_required, current_user
from models.bio_link_entries import CreateBioLinkEntries
from utils import (
    get_platform,
    generate_and_save_qr,
    update_qr_code,
    customize_qr_code_logo,
    customize,
    get_urls_by_date,
    get_qr_codes_by_date,
    get_bio_page_by_date,
)
from models.create_bio_page import CreateBioPage
from models.qr_code import QrCode
from models.user import update_otp
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from PIL import Image
from sqlalchemy import func, extract

user_blp = Blueprint("user_blp", __name__)


@user_blp.route("/", methods=["GET", "POST"])
def home():
    # form = GenerateBrandName()
    # posts = CreateProfile.query.all()
    if current_user.is_authenticated:
        return redirect(url_for("user_blp.dashboard"))
    if request.method == "POST" and "bt1" in request.form:
        original_url = request.form.get("url")
        if not original_url:
            flash("Input Required", "danger")
            return redirect(url_for("user_blp.home"))
        if not original_url.startswith("http://") and not original_url.startswith(
            "https://"
        ):
            original_url = "http://" + original_url
        check_if_exist = Urlshort.query.filter_by(url=original_url).first()
        if check_if_exist:
            print("url already exist")
            return render_template(
                "index.html",
                shortened_url=f"{request.host_url}{check_if_exist.short_url}",
                original_url=original_url,
                show=1,
                created=check_if_exist.created.strftime("%d, %b %Y %H:%M:%S"),
            )
        short_url = generate_short_url()

        url = Urlshort(
            url=original_url,
            short_url=short_url,
        )
        url.save()
        # flash('URL has been shortened successfully!', 'success')
        return render_template(
            "index.html",
            shortened_url=f"{request.host_url}{short_url}",
            original_url=original_url,
            show=1,
            created=url.created.strftime("%d, %b %Y %H:%M:%S"),
        )
    elif request.method == "POST" and "bt2" in request.form:
        brand_name = request.form.get("brandname").lower()
        if not brand_name:
            flash("Input Required", "danger")
            return redirect(url_for("user_blp.home"))
        user_ = User.query.filter_by(brand_name=brand_name).first()
        if user_:
            # User with that brand already exists
            flash("Brand Name already exists!", "danger")
            return redirect(url_for("user_blp.home"))
        return redirect(url_for("auth_blp.register", brandie=brand_name))
    return render_template("index.html")


@user_blp.route("/user/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    try:
        user_id = current_user.id
        brand_url = f"{request.host_url}{current_user.brand_name}"
        posts = CreateProfile.query.filter_by(author_id=user_id).all()

        url_short = Urlshort.query.filter_by(author_id=user_id).all()

        qr_codes_ = QrCode.query.filter_by(author_id=user_id).all()

        host_url = request.host_url
        brandie = current_user.brand_name

        for qr in current_user.qr_code:
            qr.qr_data = base64.b64encode(qr.qr_data).decode("utf-8")

        return render_template(
            "dashboard.html",
            brand_url=brand_url,
            brandie=brandie,
            host_url=host_url,
            url_short=url_short,
            qr_codes_=qr_codes_,
            dashboard=True,
        )
    except Exception as e:
        print(e, "error@dashboard")
        db.session.rollback()


@user_blp.route("/join", methods=["GET", "POST"])
def join():
    # Every render_template has a logged_in variable set.
    form = GenerateBrandName()
    if request.method == "POST":
        brand_name = request.form.get("brandname")
        user_ = User.query.filter_by(brand_name=brand_name).first()
        if user_:
            # User already exists
            flash("Brand Name already exists!")
            return redirect(url_for("home"))

        new_user = User(brand_name=brand_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("auth_blp.register"))
    return render_template("join.html", form=form, current_user=current_user)


@user_blp.route("/createBioPage", methods=["GET", "POST"])
@login_required
def create_Bio_Page():
    # Create Bio Pages.
    form = GenerateBrandName()
    if request.method == "POST":
        bio_name = request.form.get("brandname")
        if not bio_name:
            flash("Input Required", "danger")
            return redirect(url_for("user_blp.create_Bio_Page"))
        if " " in bio_name:
            flash("Bio Name cannot contain spaces", "danger")
            return redirect(url_for("user_blp.create_Bio_Page"))
        user_ = CreateBioPage.query.filter_by(bio_name=bio_name).first()
        if user_:
            # User already exists
            flash("Name already exists! Choose a unique name", "danger")
            return render_template(
                "createBioPage.html", form=form, current_user=current_user
            )

        new_user = CreateBioPage(bio_name=bio_name, author_id=current_user.id)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("user_blp.bio_link_pages", bio_id=new_user.id))
    return render_template("createBioPage.html", form=form, current_user=current_user)


# Edit Bio Name
@user_blp.route("/biolinkpages/<path:sub_path>/edit_name", methods=["GET", "POST"])
@login_required
def edit_bio(sub_path):
    # form = GenerateBrandName()
    b = CreateBioPage.query.filter_by(
        bio_name=sub_path, author_id=current_user.id
    ).first()
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_id=b.id
    ).all()
    # brandname = request.form.get("brandname")
    # if not brandname:
    #     flash("Input Required", "danger")
    #     return redirect(url_for("user_blp.dashboard"))
    # user_ = User.query.filter_by(brand_name=brandname.lower()).first()
    # if user_:
    #     # User with that brand already exists
    #     flash("Brand Name already exists!", "danger")
    #     return redirect(url_for("user_blp.dashboard"))
    # current_user.brand_name = brandname.lower()
    # db.session.commit()
    # flash("Brand Name updated successfully!", "success")
    return redirect(url_for("user_blp.bio_link_pages_details", links_added=bio_links))


# list all bio pages
@user_blp.route("/BioLinkPages", methods=["GET", "POST"])
@login_required
def bio_link_pages():
    user_name = current_user.username
    bio_pages = CreateBioPage.query.filter_by(author_id=current_user.id).all()
    bio_links = CreateBioLinkEntries.query.filter_by(author_id=current_user.id).all()
    host_url = request.host_url

    display = True if bio_pages else False
    refresh = False

    if request.method == "POST":
        date_filter = request.form.get("date")
        print(date_filter, "date")

        bio_pages = get_bio_page_by_date(date_filter)
        display = True
        refresh = True
    print(bio_pages, "Pages bio")
    # update the bio name
    return render_template(
        "BioLinkPages.html",
        host_url=host_url,
        bio_pages=bio_pages,
        links_added=bio_links,
        display=display,
        refresh=refresh,
        bio=True,
    )


@user_blp.route("/BioLinkPages/<bio_id>", methods=["POST"])
@login_required
def update_bio_link_pages(bio_id):
    brandname = request.form.get("brandname")
    if not brandname:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.bio_link_pages"))
    brand_n = CreateBioPage.query.filter_by(bio_name=brandname.lower()).first()
    brand_name = CreateBioPage.query.filter_by(
        id=bio_id, author_id=current_user.id
    ).first()
    if brand_n and brand_name.bio_name.lower() != brandname.lower():
        # User with that brand already exists
        flash("Bio Name already exists!", "danger")
        return redirect(url_for("user_blp.bio_link_pages"))
    brand_name.bio_name = brandname.lower()
    db.session.commit()
    flash("Bio Name updated successfully!", "success")
    return redirect(url_for("user_blp.bio_link_pages"))


@user_blp.route("/bio/update/<bio_id>", methods=["POST"])
@login_required
def update_details(bio_id):
    brandname = request.form.get("brandname")
    print(bio_id, "idddd")
    if not brandname:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.bio_link_pages"))
    brand_n = CreateBioPage.query.filter_by(bio_name=brandname.lower()).first()
    brand_name = CreateBioPage.query.filter_by(
        id=bio_id, author_id=current_user.id
    ).first()
    if brand_n and brand_name.bio_name.lower() != brandname.lower():
        # User with that brand already exists
        flash("Bio Name already exists!", "danger")
        return redirect(url_for("user_blp.bio_link_pages"))
    brand_name.bio_name = brandname.lower()
    db.session.commit()
    flash("Bio Name updated successfully!", "success")
    return redirect(url_for("user_blp.bio_link_pages_details", bio_id=bio_id))


@user_blp.route("/biolinkpages/<bio_id>/build", methods=["GET", "POST"])
@login_required
def bio_link_pages_details(bio_id):
    form = CreatePostForm()
    # bio_pages = CreateBioPage.query.filter_by(author_id=current_user.id).all()
    host_url = request.host_url
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_id=bio_id
    ).all()
    bios = CreateBioPage.query.filter_by(id=bio_id, author_id=current_user.id).all()

    user_id = current_user.id
    if request.method == "POST":
        linkname = form.linkname.data.lower()
        link = form.link.data.lower()

        if not linkname:
            flash("Link Name Required", "danger")
            return redirect(url_for("user_blp.bio_link_pages_details"))
        if not link:
            flash("Link Required", "danger")
            return redirect(url_for("user_blp.bio_link_pages_details"))

        if " " in linkname:
            flash("Link Name cannot contain spaces", "danger")
            return redirect(url_for("user_blp.bio_link_pages_details"))

        if not link.startswith("http://") and not link.startswith("https://"):
            link = "http://" + link

        # if not linkname:
        #     flash("Link Name Required", "danger")
        #     return redirect(url_for("user_blp.admin"))

        check_if_linkname_exists = CreateBioLinkEntries.query.filter_by(
            link_name=linkname
        ).first()
        if check_if_linkname_exists:
            flash("Link Name already exists!", "danger")
            # return redirect(url_for("user_blp.bio_link_pages_details"))

        new_post = CreateBioLinkEntries(
            link_name=linkname, link_url=link, author_id=user_id, bio_page_id=bio_id
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Link Added", "success")
        return redirect(url_for("user_blp.bio_link_pages_details", bio_id=bio_id))

    return render_template(
        "bio_link_pages_details.html",
        bio=True,
        bios=bios,
        links_added=bio_links,
        form=form,
        current_user=current_user,
        host_url=host_url,
        bio_pages=bios,
        bio_id=bio_id,
    )


@user_blp.route("/biolinkpages/<bio_id>/<parent_id>/update", methods=["POST"])
@login_required
def update_bio_link_pages_details(bio_id, parent_id):
    link_name = request.form.get("link_name")
    link_url = request.form.get("link_url")
    if not link_name:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.bio_link_pages_details", bio_id=parent_id))
    if not link_url:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.bio_link_pages_details", bio_id=parent_id))
    if not link_url.startswith("http://") and not link_url.startswith("https://"):
        link_url = "http://" + link_url
    link_n = CreateBioLinkEntries.query.filter_by(id=bio_id).first()
    if link_n:
        link_n.link_name = link_name.lower()
        link_n.link_url = link_url
        db.session.commit()
        flash("Link updated successfully!", "success")
        return redirect(url_for("user_blp.bio_link_pages_details", bio_id=parent_id))
    flash("Link does not exist!", "danger")
    return redirect(url_for("user_blp.bio_link_pages_details", bio_id=parent_id))


@user_blp.route("/bio/<brand_name>/", methods=["GET", "POST"])
# @login_required
def bio_link_routes(brand_name):
    bio_links = (
        CreateBioLinkEntries.query.join(CreateBioPage)
        .filter(func.lower(CreateBioPage.bio_name) == brand_name.lower())
        .all()
    )

    url_id = get_bio_page_id(brand_name)

    save_bio_page_clicks(url_id)
    update_bio_page_clicks(url_id)
    return render_template(
        "bio_link_routes.html", brandie=brand_name.upper(), all_posts=bio_links
    )


@user_blp.route("/biolinkpages/<bio_id>/customize/appearance", methods=["GET", "POST"])
@login_required
def bio_link_page_appearance(bio_id):
    form = CreatePostForm()
    host_url = request.host_url
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_id=bio_id
    ).all()
    bios = CreateBioPage.query.filter_by(id=bio_id, author_id=current_user.id).all()

    user_id = current_user.id
    return render_template(
        "bio_link_page_appearance.html",
        bio=True,
        bio_id=bio_id,
        bios=bios,
        links_added=bio_links,
        form=form,
        current_user=current_user,
        host_url=host_url,
    )


@user_blp.route("/biolinkpages/<bio_id>/track/analytics", methods=["GET", "POST"])
@login_required
def bio_link_page_track_analytics(bio_id):
    form = CreatePostForm()
    host_url = request.host_url
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_id=bio_id
    ).all()
    bios = CreateBioPage.query.filter_by(id=bio_id, author_id=current_user.id).all()

    user_id = current_user.id

    # Prepare data for the charts
    bio_pages = CreateBioPage.query.filter_by(author_id=user_id).all()

    # Prepare data for the charts
    bio_page_clicks = sum(bio_page.clicks for bio_page in bio_pages)

    bio_pages_generated = len(bio_pages)

    return render_template(
        "bio_link_page_track_analytics.html",
        bio=True,
        bio_id=bio_id,
        bios=bios,
        links_added=bio_links,
        form=form,
        current_user=current_user,
        host_url=host_url,
        bio_page_clicks=bio_page_clicks,
        bio_pages_generated=bio_pages_generated,
    )


@user_blp.route("/redirect")
@login_required
def redirect_me():
    return render_template("redirect.html")


# @user_blp.route("/user/admin", methods=["GET", "POST"])
# @login_required
# def admin():
#     form = CreatePostForm()
#     join_form = GenerateBrandName()
#     user_id = current_user.id
#     brand_url = f"{request.host_url}brand/{current_user.brand_name}"
#     posts = CreateProfile.query.filter_by(author_id=user_id).all()
#     brandname = current_user.brand_name
#     # if brandname is None:
#     #     flash("Please Create A Brand name")
#     #     return render_template("join.html", form=join_form, current_user=current_user)
#
#     if request.method == "POST":
#         linkname = form.linkname.data.lower()
#         link = form.link.data.lower()
#
#         if not linkname:
#             flash("Link Name Required", "danger")
#             return redirect(url_for("user_blp.admin"))
#         if not link:
#             flash("Link Required", "danger")
#             return redirect(url_for("user_blp.admin"))
#
#         if not link.startswith("http://") and not link.startswith("https://"):
#             link = "http://" + link
#
#         # if not linkname:
#         #     flash("Link Name Required", "danger")
#         #     return redirect(url_for("user_blp.admin"))
#
#         check_if_linkname_exists = CreateProfile.query.filter_by(
#             linkname=linkname
#         ).first()
#         if check_if_linkname_exists:
#             flash("Link Name already exists!", "danger")
#             return redirect(url_for("user_blp.admin"))
#
#         new_post = CreateProfile(
#             linkname=linkname,
#             link=link,
#             link_name=get_platform(link),
#             author=current_user,
#             author_id=user_id,
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         flash("Link Added", "success")
#         return redirect(url_for("user_blp.display_biolinks"))
#     return render_template(
#         "admin.html",
#         name=current_user.username.title(),
#         logged_in=True,
#         form=form,
#         brand_url=brand_url,
#         brandie=brandname,
#         host_url=request.host_url,
#     )


@user_blp.route("/<path:sub_path>", methods=["GET", "POST"])
def profile(sub_path):
    requested_profile = ""
    all_profiles = User.query.all()
    for profiles in all_profiles:
        if profiles.first_name == sub_path:
            requested_profile = profiles
    return render_template(
        "profile.html", all_posts=requested_profile, current_user=current_user
    )


# @user_blp.route('/', subdomain="<brandie>")
# def brand(brandie):
#     check_brand = User.query.filter_by(brand_name=brandie.lower()).first()
#     if not check_brand:
#         return render_template("404.html")
#     return render_template("brand.html", brandie=brandie.upper())


# All Analytics page
@user_blp.route("/analytics")
@login_required
def analytics_all():

    user_id = current_user.id

    # Prepare data for the charts
    qr_codes = QrCode.query.filter_by(author_id=user_id).all()
    bio_pages = CreateBioPage.query.filter_by(author_id=user_id).all()
    url_shorts = Urlshort.query.filter_by(author_id=user_id).all()

    current_month = datetime.now().month
    current_year = datetime.now().year

    # Query to get clicks for each day of the current month and year
    clicks_per_month_s = (
        UrlShortenerClicks.query.join(
            Urlshort, Urlshort.id == UrlShortenerClicks.url_id
        )
        .filter(
            Urlshort.author_id == current_user.id,
            extract("month", UrlShortenerClicks.created) == current_month,
            extract("year", UrlShortenerClicks.created) == current_year,
        )
        .all()
    )

    click_per_month_qrcode_s = (
        QrcodeRecord.query.join(QrCode, QrCode.id == QrcodeRecord.qr_code_id)
        .filter(
            QrCode.author_id == current_user.id,
            extract("month", QrcodeRecord.date) == current_month,
            extract("year", QrcodeRecord.date) == current_year,
        )
        .all()
    )

    click_per_month_bio_s = (
        BioPageClicks.query.join(
            CreateBioPage, CreateBioPage.id == BioPageClicks.bio_page_id
        )
        .filter(
            CreateBioPage.author_id == current_user.id,
            extract("month", BioPageClicks.created) == current_month,
            extract("year", BioPageClicks.created) == current_year,
        )
        .all()
    )

    res = [
        {
            "date": clicks_per_month.created.strftime("%d-%b-%Y"),
            "clicks": clicks_per_month.count,
        }
        for clicks_per_month in clicks_per_month_s
    ]
    res2 = [
        {
            "date": clicks_per_month.date.strftime("%d-%b-%Y"),
            "clicks": clicks_per_month.clicks,
        }
        for clicks_per_month in click_per_month_qrcode_s
    ]
    res3 = [
        {
            "date": clicks_per_month.created.strftime("%d-%b-%Y"),
            "clicks": clicks_per_month.count,
        }
        for clicks_per_month in click_per_month_bio_s
    ]

    # Prepare data for the charts
    qr_code_clicks = sum(qr_code.clicks for qr_code in qr_codes)
    bio_page_clicks = sum(bio_page.clicks for bio_page in bio_pages)
    url_short_clicks = sum(url_short.clicks for url_short in url_shorts)

    qr_code_generated = len(qr_codes)
    bio_pages_generated = len(bio_pages)
    url_shorts_generated = len(url_shorts)
    return render_template(
        "analysis.html",
        analytics=True,
        qr_code_clicks=qr_code_clicks,
        bio_page_clicks=bio_page_clicks,
        url_short_clicks=url_short_clicks,
        qr_code_generated=qr_code_generated,
        bio_pages_generated=bio_pages_generated,
        url_shorts_generated=url_shorts_generated,
        res=res,
        res2=res2,
        res3=res3,
    )
    # return render_template("analytics_all.html", analytics=True)


@user_blp.route("/brand/<brandname>/", methods=["GET", "POST"])
def brand(brandname):
    check_brand = User.query.filter_by(brand_name=brandname.lower()).first()
    if not check_brand:
        return render_template("404.html")
    check_brand_posts = CreateProfile.query.filter_by(author_id=check_brand.id).all()
    return render_template(
        "brand.html", brandie=brandname.upper(), all_posts=check_brand_posts[::-1]
    )


@user_blp.route("/<brandname>/<linkname>", methods=["GET", "POST"])
def product(brandname, linkname):
    check_brand = User.query.filter_by(brand_name=brandname.lower()).first()
    if not check_brand:
        return render_template("404.html")
    check_product = CreateProfile.query.filter_by(linkname=linkname.lower()).first()
    if not check_product:
        return render_template("404.html")
    check_product.clicks += 1
    db.session.commit()
    return render_template(
        "product.html",
        brandie=brandname.upper(),
        linkname=linkname.upper(),
        check_product=check_product,
    )


# update brandname to user model
@user_blp.route("/update/brandname", methods=["POST"])
@login_required
def update_brandname():
    brandname = request.form.get("brandname")
    referer = request.headers.get("Referer")
    if not brandname:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.dashboard"))
    user_ = User.query.filter_by(brand_name=brandname.lower()).first()
    if user_ and current_user.brand_name.lower() != brandname.lower():
        # User with that brand already exists
        flash("Brand Name already exists!", "danger")
        return redirect(referer or url_for("user_blp.dashboard"))
    current_user.brand_name = brandname.lower()
    db.session.commit()
    flash("Brand Name updated successfully!", "success")
    return redirect(referer or url_for("user_blp.admin"))


@user_blp.route("/delete/<linkname>")
@login_required
def delete_product(linkname):
    check_product = CreateProfile.query.filter_by(linkname=linkname.lower()).first()
    referer = request.headers.get("Referer")
    if not check_product:
        return render_template("404.html")
    db.session.delete(check_product)
    db.session.commit()
    flash("Product deleted", "success")
    return redirect(referer or url_for("user_blp.dashboard"))


# @user_blp.route("/qr_code/stats/<int:qr_id>", methods=["GET"])
# @login_required
# def qr_code_stats(qr_id):
#     qr_codes = QrcodeRecord.query.filter_by(qr_code_id=qr_id).all()
#     if not qr_codes:
#         flash("No stats for this QR Code", "info")
#         return redirect(url_for("user_blp.display_qr_codes"))
#     # Extract dates and click counts
#     dates = [entry.date for entry in qr_codes]
#     clicks = [entry.clicks for entry in qr_codes]
#
#     # Create a simple bar chart using Matplotlib
#     plt.figure(figsize=(10, 6))
#     plt.bar(dates, clicks)
#     plt.xlabel("Date")
#     plt.ylabel("Number of Clicks")
#     plt.title("Clicks Over Time")
#
#     # Convert the plot to a PNG image
#     img = io.BytesIO()
#     plt.savefig(img, format="png")
#     img.seek(0)
#     plot_url = base64.b64encode(img.getvalue()).decode()
#     return render_template("qr_code_stats.html", plot_url=plot_url)


# SHORTEN URL SECTION
@user_blp.route("/urls/shorten_url", methods=["GET", "POST"])
@login_required
def shorten_url():
    if request.method == "POST":
        print("got hereeeee")
        original_url = request.form.get("originalUrl")
        custom_url = request.form.get("customUrl", None)
        title = (
            request.form.get("title")
            or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )
        generate_qr_code = request.form.get("check_box", "")

        generate_qr_code = True if generate_qr_code == "on" else False

        print(
            f"original_url: {original_url}, custom_url: {custom_url}, title: {title}, generate_qr_code: {generate_qr_code}"
        )

        # if Urlshort.query.filter_by(
        #         author_id=current_user.id, url=original_url
        # ).first():
        #     flash("URL already exists", "danger")
        #     return render_template("shorten.html")
        # if not validate_url(original_url):
        # flash('Please enter a valid URL', 'danger')
        # return render_template("shorten.html")

        if custom_url:
            print(custom_url, "custom_url")
            short_url = custom_url
            if Urlshort.query.filter_by(short_url=short_url).first():
                flash("Custom URL already exists", "danger")
                print("Custom URL already exists")
                return render_template("shorten.html")
        else:
            short_url = generate_short_url()

        url_and_short_url = f"{request.host_url}{short_url}"

        res = generate_and_save_qr(url_and_short_url) if generate_qr_code else ""
        # print(res, 'res')

        url = Urlshort(
            author=current_user,
            author_id=current_user.id,
            url=original_url,
            short_url=short_url,
            title=title,
            qr_data=res,
            want_qr_code=generate_qr_code,
        )
        url.save()
        flash("URL has been shortened successfully!", "success")
        return render_template(
            "shorten.html",
            shortened_url=f"{request.host_url}{short_url}",
            original_url=original_url,
            generate_qr_code=generate_qr_code,
            done_creating=True,
            qr_data=base64.b64encode(res).decode("utf-8") if res else res,
        )

    return render_template("shorten.html", done_creating=False)


# redirect short url to the original url
@user_blp.route("/<short_url>/")
def redirect_to_url(short_url):
    current_date = datetime.now().strftime("%d-%m-%Y")
    print(current_date, "current date")
    if short_url == "qr-code":
        return redirect(url_for("user_blp.qr_code_info"))
    if short_url == "url-shortener":
        return redirect(url_for("user_blp.url_shortener_info"))
    if short_url == "biolink":
        return redirect(url_for("user_blp.biolink"))
    url = Urlshort.query.filter_by(short_url=short_url).first()
    if not url:
        url = QrCode.query.filter_by(short_url=short_url).first()
        save_qrcode_clicks(url.id)
    else:
        save_url_clicks(url.id)

    url.clicks += 1
    db.session.commit()
    print(url.url, "the real url")
    return redirect(url.url)


# display all shortened urls with their original urls and clicks
@user_blp.route("/stats/urls", methods=["GET", "POST"])
@login_required
def display_urls():
    urls = Urlshort.query.filter_by(author_id=current_user.id).all()
    display = True if urls else False
    refresh = False
    for qr in urls:
        qr.qr_data = (
            base64.b64encode(qr.qr_data).decode("utf-8") if qr.qr_data else qr.qr_data
        )
        print(qr.created, "date created")

    if request.method == "POST":
        date_filter = request.form.get("date")
        print(date_filter, "date")

        urls = get_urls_by_date(date_filter)
        display = True
        refresh = True

    return render_template(
        "urls.html", urls=urls, display=display, refresh=refresh, link=True
    )


# delete a shortened url
@user_blp.route("/urls/delete/<int:url_id>")
@login_required
def delete_url(url_id):
    # check if the url exists and if its for the current user
    url = Urlshort.query.filter_by(id=url_id, author_id=current_user.id).first_or_404()
    referer = request.headers.get("Referer")
    db.session.delete(url)
    db.session.commit()
    flash("URL deleted", "success")
    return redirect(referer or url_for("user_blp.display_urls"))


#        QR CODE SECTION
# This is the page to display all the qr codes for the current user
@user_blp.route("/qr_codes/create", methods=["GET", "POST"])
@login_required
def qr_codes():
    if request.method == "POST":
        url = request.form.get("url")
        title = (
            request.form.get("title")
            or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )
        if not url:
            flash("Please enter a URL", "danger")
            return render_template("qr_codes.html")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # generate short url for the url
        short_ur = generate_short_url2()

        gr_dat = f"{request.host_url}{short_ur}"

        res = generate_and_save_qr(gr_dat)

        # check if the url exists
        existing_qr_code = QrCode.query.filter_by(
            author_id=current_user.id, url=url
        ).first()
        if existing_qr_code:
            flash("QR Code already exists", "danger")
            return render_template("qr_codes.html", n=1, url=existing_qr_code.url)
        new_qr_code = QrCode(
            author=current_user,
            author_id=current_user.id,
            url=url,
            qr_data=res,
            short_url=generate_short_url2(),
            title=title,
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes.html", n=0, qr=True)


# QR Codes for Email
@user_blp.route("/qr_codes/create_email", methods=["GET", "POST"])
@login_required
def qr_codes_email():
    if request.method == "POST":
        email = request.form.get("email")
        title = (
            request.form.get("title")
            or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )
        res = generate_and_save_qr(email)
        # check if the url exists
        existing_qr_code = QrCode.query.filter_by(
            author_id=current_user.id, email=email
        ).first()
        if existing_qr_code:
            flash("Email already exists", "danger")
            return render_template("qr_codes_email.html", n=1, url=existing_qr_code.url)
        new_qr_code = QrCode(
            author=current_user,
            author_id=current_user.id,
            email=email,
            qr_data=res,
            short_url=generate_short_url2(),
            title=title,
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes_email.html", n=0, qr=True)


# QR Codes for Email
@user_blp.route("/qr_codes/create_vcard", methods=["GET", "POST"])
@login_required
def qr_codes_vcard():
    if request.method == "POST":
        title = (
            request.form.get("title")
            or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )
        name = request.form.get("name")
        org = request.form.get("org")
        phone = request.form.get("phone")
        website = request.form.get("website")
        mail = request.form.get("mail")
        address = request.form.get("address")
        note = request.form.get("note")

        data = dict(
            name=name,
            org=org,
            phone=phone,
            website=website,
            mail=mail,
            address=address,
            note=note,
        )

        res = generate_and_save_qr(data)

        # check if the url exists
        existing_qr_code = QrCode.query.filter_by(
            author_id=current_user.id, mail=mail
        ).first()
        if existing_qr_code:
            flash("Email already exists", "danger")
            return render_template("qr_codes_email.html", n=1, url=existing_qr_code.url)
        new_qr_code = QrCode(
            author=current_user,
            author_id=current_user.id,
            short_url=generate_short_url2(),
            qr_data=res,
            title=title,
            name=name,
            org=org,
            phone=phone,
            website=website,
            address=address,
            mail=mail,
            note=note,
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes_vcard.html", n=0, qr=True)


# QR Codes for WIFI
@user_blp.route("/qr_codes/create_wifi", methods=["GET", "POST"])
@login_required
def qr_codes_wifi():
    if request.method == "POST":
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        title = (
            request.form.get("title")
            or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        )

        hash_and_salted_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=3
        )

        data = dict(
            ssid=ssid,
            password=hash_and_salted_password,
        )
        res = generate_and_save_qr(data)
        # check if the url exists
        existing_qr_code = QrCode.query.filter_by(
            author_id=current_user.id, ssid=ssid
        ).first()
        if existing_qr_code:
            flash("Wifi already exists", "danger")
            return render_template("qr_codes_wifi.html", n=1, url=existing_qr_code.url)
        new_qr_code = QrCode(
            author=current_user,
            author_id=current_user.id,
            ssid=ssid,
            password=password,
            qr_data=res,
            short_url=generate_short_url2(),
            title=title,
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes_wifi.html", n=0, qr=True)


# display all qr codes for the current user
@user_blp.route("/stats/qr_codes", methods=["GET", "POST"])
@login_required
def display_qr_codes():
    qrcodes = QrCode.query.filter_by(author_id=current_user.id).all()
    display = True if qrcodes else False
    refresh = False
    for qr in qrcodes:
        qr.qr_data = base64.b64encode(qr.qr_data).decode("utf-8")

    if request.method == "POST":
        date_filter = request.form.get("date")
        print(date_filter, "date")

        qrcodes = get_qr_codes_by_date(date_filter)
        display = True
        refresh = True
    return render_template(
        "display_qr.html", urls=qrcodes, display=display, refresh=refresh, qr=True
    )


# View all qr codes details for the current user
@user_blp.route("/stats/qr_codes/details/<int:qr_id>", methods=["GET"])
@login_required
def qr_codes_details(qr_id):
    # qrcodes = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).all()
    # qr_codes = QrcodeRecord.query.filter_by(qr_code_id=qr_id).all()
    # if not qr_codes:
    #     flash('No stats for this QR Code', 'info')
    #     return redirect(url_for('user_blp.display_qr_codes'))
    # Extract dates and click counts
    # dates = [entry['date'] for entry in qr_codes]
    # clicks = [entry['clicks'] for entry in qr_codes]

    # qrcodes = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).all()
    # # Extract dates and click counts
    # dates = [entry['date'] for entry in click_data]
    # clicks = [entry['clicks'] for entry in click_data]
    #
    # # Create a simple bar chart using Matplotlib
    # plt.figure(figsize=(10, 6))
    # plt.bar(dates, clicks)
    # plt.xlabel('Date')
    # plt.ylabel('Number of Clicks')
    # plt.title('Clicks Over Time')
    #
    # # Convert the plot to a PNG image
    # img = io.BytesIO()
    # plt.savefig(img, format='png')
    # img.seek(0)
    # plot_url = base64.b64encode(img.getvalue()).decode()
    # return render_template("qr_codes_details.html", urls=qrcodes, plot_url=plot_url)

    qrcodes = QrCode.query.filter_by(
        id=qr_id, author_id=current_user.id
    ).all()  # check if this should be .all or .first
    qr_codes = QrcodeRecord.query.filter_by(qr_code_id=qr_id).all()
    # if not qr_codes:
    #     print("No stats for this QR Code")
    #     flash("No stats for this QR Code", "info")
    #     return redirect(url_for("user_blp.display_qr_codes"))
    # Extract dates and click counts
    dates = [entry.date for entry in qr_codes]
    clicks = [entry.clicks for entry in qr_codes]

    # Create a simple bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(dates, clicks)
    plt.xlabel("Date")
    plt.ylabel("Number of Clicks")
    plt.title("Clicks Over Time")

    # Convert the plot to a PNG image
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    # return render_template("qr_codes_details.html", urls=qrcodes, plot_url=plot_url)
    return render_template(
        "qr_codes_details.html", urls=qrcodes, plot_url=plot_url, qr=True
    )


#            Customize QR CODES
@user_blp.route("/qr_codes/customize/<int:qr_id>", methods=["GET", "POST"])
@login_required
def qr_codes_customize(qr_id):
    qrcode = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).first()
    qrcode.qr_data = base64.b64encode(qrcode.qr_data).decode("utf-8")
    if request.method == "POST":
        try:
            qrcode = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).first()
            color = request.form.get("color")
            # get the image data
            logo = request.files["image"]
            social_media_logo = request.form.get("placeholder_images")
            print(logo, "LOGO")
            print(social_media_logo, "social_media_logo")
            if logo and social_media_logo:
                flash("Please select either logo or social media logo", "danger")
                return redirect(url_for("user_blp.qr_codes_customize", qr_id=qr_id))
            if social_media_logo and social_media_logo == "youtube":
                # use the png in the static folder as logo
                logo = "static/yt.png"
            elif social_media_logo and social_media_logo == "twitter":
                # use the png in the static folder as logo
                logo = "static/tw.png"
            elif social_media_logo and social_media_logo == "facebook":
                # use the png in the static folder as logo
                logo = "static/fb.png"
            elif social_media_logo and social_media_logo == "instagram":
                # use the png in the static folder as logo
                logo = "static/ig.png"
            if qrcode.url:
                data = qrcode.url
            elif qrcode.email:
                data = qrcode.email
            else:
                data = dict(
                    name=qrcode.name,
                    org=qrcode.org,
                    phone=qrcode.phone,
                    website=qrcode.website,
                    mail=qrcode.email,
                    address=qrcode.address,
                    note=qrcode.note,
                )
            # data = qrcode.url if qrcode.url else qrcode.email
            res = (
                update_qr_code(data, color)
                if color and not logo
                else customize(data, logo, color)
            )
            qrcode.qr_data = res
            db.session.commit()
            return redirect(url_for("user_blp.qr_codes_customize", qr_id=qr_id))
        except Exception as e:
            print(e, "this is the error")
            db.session.rollback()
            return redirect(url_for("user_blp.qr_codes_customize", qr_id=qr_id))
    return render_template("qr_codes_customize.html", qrcode=qrcode, qr=True)


#                    Edit QR CODES
@user_blp.route("/qr_codes/edit/<int:qr_id>/contents", methods=["GET", "POST"])
@login_required
def qr_codes_content_edit(qr_id):
    qrcodes = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).all()
    datas = []
    for qr in qrcodes:
        if qr.url or qr.email:
            pass
        else:
            datas.append(
                {
                    "name": qr.name,
                    "org": qr.org,
                    "phone": qr.phone,
                    "mail": qr.mail,
                    "website": qr.website,
                    "address": qr.address,
                    "note": qr.note,
                }
            )

    return render_template(
        "qr_codes_content_edit.html", urls=qrcodes, datas=datas, qr=True
    )


# delete a qr code
@user_blp.route("/qr_codes/delete/<int:qr_id>", methods=["GET"])
@login_required
def delete_qr_code(qr_id):
    # check if the qr code exists and if it's for the current user
    qrcode = QrCode.query.filter_by(id=qr_id, author_id=current_user.id).first_or_404()
    referer = request.headers.get("Referer")
    qrcode.delete()
    flash("QR Code deleted", "success")
    return redirect(referer or url_for("user_blp.display_qr_codes"))


# qr code for all users (logged in or not )
@user_blp.route("/qr-code")
def qr_code_info():
    return render_template("qr_code_info.html")


@user_blp.route("/biolink")
def biolink():
    return render_template("biolink.html")


@user_blp.route("/url-shortener")
def url_shortener_info():
    return render_template("url_shortener_info.html")


@user_blp.route("/profile/<username>")
@login_required
def profile_info(username):
    return render_template("profile_info.html")


# list all bio links
@user_blp.route("/biolinks", methods=["GET"])
@login_required
def display_biolinks():
    biolinks = CreateProfile.query.filter_by(author_id=current_user.id).all()
    brand_url = f"{request.host_url}{current_user.brand_name}"
    return render_template("biolinks.html", biolinks=biolinks, brand_url=brand_url)


@user_blp.route("/see", methods=["GET"])
def see():
    return render_template("base2.html")


# @user_blp.route('/qrqr', methods=['GET'])
# def qrqr():
#     data_to_encode = "https://www.youtube.com/watch?v=QH2-TGUlwu4"
#
#     # Generate QR code
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data_to_encode)
#     qr.make(fit=True)
#
#     # Create an image from the QR Code instance
#     img = qr.make_image(fill_color="black", back_color="white")
#
#     # Save the image to BytesIO
#     img_bytes_io = BytesIO()
#     img.save(img_bytes_io)
#     img_bytes_io.seek(0)
#
#     # Save the image to the database
#     qr_code_data = QRCodeData(qr_code_image=img_bytes_io.read())
#     db.session.add(qr_code_data)
#     db.session.commit()
#     return "DONE"
#
#
# @user_blp.route('/qrqr2', methods=['GET'])
# def qrqr2():
#     # Query the database for the latest QR code data
#     latest_qr_code_data = QRCodeData.query.order_by(QRCodeData.id.desc()).all()
#
#     if latest_qr_code_data:
#         # Convert the binary image data to a base64-encoded string
#         base64_image = base64.b64encode(latest_qr_code_data.qr_code_image).decode('utf-8')
#
#         # Pass the base64-encoded image data to the template
#         return render_template('grgr.html', qr_code_image=base64_image)
#
#     return "No QR code data found."
