from urllib import request
from urllib.error import HTTPError, URLError


# def validate_url(url):
#     if not url.startswith('http://') and not url.startswith('https://'):
#         url = 'http://' + url
#     try:
#         request.urlopen(url)
#         return True
#     except (HTTPError, URLError):
#         return False


def check_if_amazon_url_is_valid(url):
    if "amazon" in url:
        return True
    else:
        return False


def check_if_youtube_url_is_valid(url):
    if "youtube" in url:
        return True
    else:
        return False


def check_if_twitter_url_is_valid(url):
    if "twitter" in url:
        return True
    else:
        return False


def check_if_facebook_url_is_valid(url):
    if "facebook" in url or "fb" in url:
        return True
    else:
        return False
