from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from forms import *
from models import *
from extensions import db
from flask_login import login_user, login_required, current_user
from models.bio_link_entries import CreateBioLinkEntries
from utils import get_platform
from models.create_bio_page import CreateBioPage
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

user_blp = Blueprint("user_blp", __name__)


@user_blp.route("/", methods=["GET", "POST"])
def home():
    # form = GenerateBrandName()
    # posts = CreateProfile.query.all()
    if current_user.is_authenticated:
        return redirect(url_for("user_blp.admin"))
    if request.method == "POST" and "bt1" in request.form:
        original_url = request.form.get("url")
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
    user_id = current_user.id
    brand_url = f"{request.host_url}{current_user.brand_name}"
    posts = CreateProfile.query.filter_by(author_id=user_id).all()

    url_short = Urlshort.query.filter_by(author_id=user_id).all()

    qr_codes_ = QrCode.query.filter_by(author_id=user_id).all()

    host_url = request.host_url
    brandie = current_user.brand_name
    return render_template(
        "dashboard.html",
        brand_url=brand_url,
        brandie=brandie,
        host_url=host_url,
        url_short=url_short,
        qr_codes_=qr_codes_,
    )


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
        return redirect(url_for("user_blp.bio_link_pages"))
    return render_template("createBioPage.html", form=form, current_user=current_user)


# Edit Bio Name
@user_blp.route("/biolinkpages/<path:sub_path>/edit_name", methods=["GET", "POST"])
@login_required
def edit_bio(sub_path):
    form = GenerateBrandName()
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_name=sub_path
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
    return redirect(url_for("user_blp.bio_link_pages_details", form=form, links_added=bio_links, sub_path=sub_path))


# list all bio pages
@user_blp.route("/BioLinkPages", methods=["GET", "POST"])
@login_required
def bio_link_pages():
    user_name = current_user.username
    bio_pages = CreateBioPage.query.filter_by(author_id=current_user.id).all()
    bio_links = CreateBioLinkEntries.query.filter_by(author_id=current_user.id).all()
    host_url = request.host_url
    # update the bio name
    return render_template(
        "BioLinkPages.html", host_url=host_url, bio_pages=bio_pages, links_added=bio_links
    )


@user_blp.route("/BioLinkPages/<bio_id>", methods=["POST"])
@login_required
def update_bio_link_pages(bio_id):
    brandname = request.form.get("brandname")
    if not brandname:
        flash("Input Required", "danger")
        return redirect(url_for("user_blp.bio_link_pages"))
    brand_n = CreateBioPage.query.filter_by(
        bio_name=brandname.lower()
    ).first()
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

@user_blp.route("/biolinkpages/<path:sub_path>/build", methods=["GET", "POST"])
@login_required
def bio_link_pages_details(sub_path):
    form = CreatePostForm()
    bio_pages = CreateBioPage.query.filter_by(author_id=current_user.id).all()
    host_url = request.host_url
    bio_links = CreateBioLinkEntries.query.filter_by(
        author_id=current_user.id, bio_page_name=sub_path
    ).all()
    bios = CreateBioPage.query.filter_by(
        bio_name=sub_path, author_id=current_user.id
    ).all()

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
            link_name=linkname, link_url=link, author_id=user_id, bio_page_name=sub_path
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Link Added", "success")
        return redirect(url_for('user_blp.bio_link_pages_details', sub_path=sub_path))
        # return render_template(
        #     "bio_link_pages_details.html",
        #     bios=bios,
        #     links_added=bio_links,
        #     form=form,
        #     current_user=current_user,
        # )
    return render_template(
        "bio_link_pages_details.html",
        bios=bios,
        links_added=bio_links,
        form=form,
        current_user=current_user,
        host_url=host_url,
        bio_pages=bios
    )


@user_blp.route("/bio/<brand_name>/", methods=["GET", "POST"])
def bio_link_routes(brand_name):
    check_brand = CreateBioPage.query.filter_by(bio_name=brand_name.lower()).first()
    if not check_brand:
        return render_template("404.html")
    bio_links = CreateBioLinkEntries.query.filter_by(bio_page_name=brand_name).all()
    return render_template(
        "bio_link_routes.html", brandie=brand_name.upper(), all_posts=bio_links
    )


@user_blp.route("/redirect")
@login_required
def redirect_me():
    return render_template("redirect.html")


@user_blp.route("/user/admin", methods=["GET", "POST"])
@login_required
def admin():
    form = CreatePostForm()
    join_form = GenerateBrandName()
    user_id = current_user.id
    brand_url = f"{request.host_url}brand/{current_user.brand_name}"
    posts = CreateProfile.query.filter_by(author_id=user_id).all()
    brandname = current_user.brand_name
    # if brandname is None:
    #     flash("Please Create A Brand name")
    #     return render_template("join.html", form=join_form, current_user=current_user)

    if request.method == "POST":
        linkname = form.linkname.data.lower()
        link = form.link.data.lower()

        if not linkname:
            flash("Link Name Required", "danger")
            return redirect(url_for("user_blp.admin"))
        if not link:
            flash("Link Required", "danger")
            return redirect(url_for("user_blp.admin"))

        if not link.startswith("http://") and not link.startswith("https://"):
            link = "http://" + link

        # if not linkname:
        #     flash("Link Name Required", "danger")
        #     return redirect(url_for("user_blp.admin"))

        check_if_linkname_exists = CreateProfile.query.filter_by(
            linkname=linkname
        ).first()
        if check_if_linkname_exists:
            flash("Link Name already exists!", "danger")
            return redirect(url_for("user_blp.admin"))

        new_post = CreateProfile(
            linkname=linkname,
            link=link,
            link_name=get_platform(link),
            author=current_user,
            author_id=user_id,
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Link Added", "success")
        return redirect(url_for("user_blp.display_biolinks"))
    return render_template(
        "admin.html",
        name=current_user.username.title(),
        logged_in=True,
        form=form,
        brand_url=brand_url,
        brandie=brandname,
        host_url=request.host_url,
    )


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


@user_blp.route("/qr_code/stats/<int:qr_id>", methods=["GET"])
@login_required
def qr_code_stats(qr_id):
    qr_codes = QrcodeRecord.query.filter_by(qr_code_id=qr_id).all()
    if not qr_codes:
        flash("No stats for this QR Code", "info")
        return redirect(url_for("user_blp.display_qr_codes"))
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
    return render_template("qr_code_stats.html", plot_url=plot_url)


# SHORTEN URL SECTION
@user_blp.route("/urls/shorten_url", methods=["GET", "POST"])
@login_required
def shorten_url():
    if request.method == "POST":
        print("got hereeeee")
        original_url = request.form.get("originalUrl")
        custom_url = request.form.get("customUrl", None)
        title = request.form.get("title") or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        generate_qr_code = request.form.get("check_box", "")

        generate_qr_code = True if generate_qr_code == "on" else False

        print(
            f"original_url: {original_url}, custom_url: {custom_url}, title: {title}, generate_qr_code: {generate_qr_code}"
        )

        if Urlshort.query.filter_by(
                author_id=current_user.id, url=original_url
        ).first():
            flash("URL already exists", "danger")
            return render_template("shorten.html")
        # if not validate_url(original_url):
        # flash('Please enter a valid URL', 'danger')
        # return render_template("shorten.html")

        if custom_url:
            short_url = custom_url
            if Urlshort.query.filter_by(short_url=short_url).first():
                flash("Custom URL already exists", "danger")
                return render_template("shorten.html")
        else:
            short_url = generate_short_url()
            print(generate_short_url())

        url = Urlshort(
            author=current_user,
            author_id=current_user.id,
            url=original_url,
            short_url=short_url,
            title=title,
            want_qr_code=generate_qr_code
        )
        url.save()
        flash("URL has been shortened successfully!", "success")
        return render_template(
            "shorten.html",
            shortened_url=f"{request.host_url}{short_url}",
            original_url=original_url, generate_qr_code=generate_qr_code
        )

    return render_template("shorten.html")


# redirect short url to the original url
@user_blp.route("/<short_url>/")
def redirect_to_url(short_url):
    current_date = datetime.now().strftime("%d-%b-%Y")
    print(current_date, "current date")
    if short_url == "qr-code":
        return redirect(url_for("user_blp.qr_code_info"))
    if short_url == "url-shortener":
        return redirect(url_for("user_blp.url_shortener_info"))
    if short_url == "biolink":
        return redirect(url_for("user_blp.biolink"))
    url = Urlshort.query.filter_by(short_url=short_url).first()
    if not url:
        url = QrCode.query.filter_by(short_url=short_url).first_or_404()
        record = QrcodeRecord.query.filter_by(
            qr_code_id=url.id, date=current_date
        ).first()
        if not record:
            new_record = QrcodeRecord(qr_code_id=url.id, date=current_date, clicks=1)
            db.session.add(new_record)
        else:
            record.clicks += 1

    url.clicks += 1
    db.session.commit()
    print(url.url)
    return redirect(url.url)


# display all shortened urls with their original urls and clicks
@user_blp.route("/stats/urls", methods=["GET"])
@login_required
def display_urls():
    urls = Urlshort.query.filter_by(author_id=current_user.id).all()
    return render_template("urls.html", urls=urls)


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


# This is the page to display all the qr codes for the current user
@user_blp.route("/qr_codes/create", methods=["GET", "POST"])
@login_required
def qr_codes():
    if request.method == "POST":
        url = request.form.get("url")
        title = request.form.get("title") or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        if not url:
            flash("Please enter a URL", "danger")
            return render_template("qr_codes.html")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

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
            short_url=generate_short_url2(),
            title=title
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes.html", n=0)


# QR Codes for Email
@user_blp.route("/qr_codes/create_email", methods=["GET", "POST"])
@login_required
def qr_codes_email():
    if request.method == "POST":
        email = request.form.get("email")
        title = request.form.get("title") or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
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
            short_url=generate_short_url2(),
            title=title
        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes_email.html", n=0)


# QR Codes for Email
@user_blp.route("/qr_codes/create_vcard", methods=["GET", "POST"])
@login_required
def qr_codes_vcard():
    if request.method == "POST":
        title = request.form.get("title") or f"Untitled {datetime.now().strftime('%Y-%m-%d %I:%M:%S %Z ')}"
        name = request.form.get("name")
        org = request.form.get("org")
        phone = request.form.get("phone")
        website = request.form.get("website")
        mail = request.form.get("mail")
        address = request.form.get("address")
        note = request.form.get("note")

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
            title=title,
            name=name,
            org=org,
            phone=phone,
            website=website,
            address=address,
            mail=mail,
            note=note

        )
        new_qr_code.save()
        flash("QR Code has been generated successfully!", "success")
        return redirect(url_for("user_blp.display_qr_codes"))
    return render_template("qr_codes_vcard.html", n=0)


# display all qr codes for the current user
@user_blp.route("/stats/qr_codes", methods=["GET"])
@login_required
def display_qr_codes():
    qrcodes = QrCode.query.filter_by(author_id=current_user.id).all()
    return render_template("display_qr.html", urls=qrcodes)


# Sample data (you should replace this with your actual data source)
# click_data = [
#     {"date": "2023-11-01", "clicks": 10},
#     {"date": "2023-11-02", "clicks": 15},
#     {"date": "2023-11-03", "clicks": 8},
#     # Add more data here
# ]


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
    if not qr_codes:
        print("No stats for this QR Code")
        flash("No stats for this QR Code", "info")
        return redirect(url_for("user_blp.display_qr_codes"))
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
    return render_template("qr_codes_details.html", urls=qrcodes, plot_url=plot_url)


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
