import re
# Importing library
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw
from models import Urlshort, QrCode, CreateBioPage
from datetime import datetime, timedelta


def get_platform(link):
    # Define regular expressions for each platform's link pattern
    platform_patterns = {
        "Facebook": r"(?:www\.)?(facebook\.com|fb\.com)",
        "Twitter": r"(?:www\.)?twitter\.com",
        "Instagram": r"(?:www\.)?instagram\.com",
        "LinkedIn": r"(?:www\.)?linkedin\.com",
        "YouTube": r"(?:www\.)?youtube\.com",
        "Threads": r"(?:www\.)?threads\.com",
        "Snapchat": r"(?:www\.)?snapchat\.com",
        "TikTok": r"(?:www\.)?tiktok\.com",
        "AppleMusic": r"(?:www\.)?applemusic\.com",
        "Audiomack": r"(?:www\.)?audiomack\.com",
        "Spotify": r"(?:www\.)?spotify\.com",
        "Boomplay": r"(?:www\.)?boomplay\.com",
        "Amazon": r"(?:www\.)?amazon\.com",
        "WhatsApp": r"(?:www\.)?whatsapp\.com",
    }

    # Check each platform's pattern
    for platform, pattern in platform_patterns.items():
        if re.search(pattern, link, re.IGNORECASE):
            return platform

    return "Other"  # If no matching platform pattern is found


def generate_and_save_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    # Save the QR code to BytesIO
    img_bytes_io = BytesIO()
    img.save(img_bytes_io, format='PNG')

    return img_bytes_io.getvalue()


def update_qr_code(data, fill_color):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color='white')

    # Save the QR code to BytesIO
    img_bytes_io = BytesIO()
    img.save(img_bytes_io, format='PNG')

    return img_bytes_io.getvalue()


def customize_qr_code_logo(data, logo_path, fill_color):
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=fill_color, back_color='white')

    # Open the logo image and resize it
    logo = Image.open(logo_path)

    # Set the maximum size you want for the logo
    basewidth = 100
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize))

    # Calculate the position to place the logo in the center
    pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

    # Paste the resized logo onto the QR code
    qr_img.paste(logo, pos)

    # Save the final image to BytesIO
    img_bytes_io = BytesIO()
    qr_img.save(img_bytes_io, format='PNG')

    return img_bytes_io.getvalue()


def customize(data, logo_path, fill_color):
    logo = Image.open(logo_path)

    # taking base width

    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))

    hsize = int((float(logo.size[1]) * float(wpercent)))

    logo = logo.resize((basewidth, hsize))

    QRcode = qrcode.QRCode(

        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    # adding URL or text to QRcode
    QRcode.add_data(data)

    # generating QR code
    QRcode.make()

    # taking color name from user

    # adding color to QR code

    QRimg = QRcode.make_image(

        fill_color=fill_color, back_color="white").convert('RGB')

    # set size of QR code

    pos = ((QRimg.size[0] - logo.size[0]) // 2,

           (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)

    # save the QR code generated as BytesIO

    img_bytes_io = BytesIO()

    QRimg.save(img_bytes_io, format='PNG')

    return img_bytes_io.getvalue()


def get_urls_by_date(selected_date):
    try:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        print(selected_datetime, "selected datetime")
        urls = Urlshort.query.filter(Urlshort.created >= selected_datetime, Urlshort.created < selected_datetime + timedelta(days=1)).all()
        return urls
    except ValueError:
        print("Invalid date format")
        # Handle invalid date format
        return []


def get_qr_codes_by_date(selected_date):
    try:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        print(selected_datetime, "selected datetime")
        qr_codes = QrCode.query.filter(QrCode.created_at >= selected_datetime, QrCode.created_at < selected_datetime + timedelta(days=1)).all()
        return qr_codes
    except ValueError:
        print("Invalid date format")
        # Handle invalid date format
        return []


def get_bio_page_by_date(selected_date):
    try:
        selected_datetime = datetime.strptime(selected_date, '%Y-%m-%d')
        print(selected_datetime, "selected datetime")
        bio_pages = CreateBioPage.query.filter(CreateBioPage.created_at >= selected_datetime, CreateBioPage.created_at < selected_datetime + timedelta(days=1)).all()
        return bio_pages
    except ValueError:
        print("Invalid date format")
        # Handle invalid date format
        return []
