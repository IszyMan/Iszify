import re
# Importing library
import qrcode
from io import BytesIO


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
    img = qr.make_image(fill_color='red', back_color='white')

    # Save the QR code to BytesIO
    img_bytes_io = BytesIO()
    img.save(img_bytes_io, format='PNG')

    return img_bytes_io.getvalue()
