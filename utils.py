#
# def check_if_url_is_valid(url):
#     try:
#         requests.get(url)
#         return True
#     except requests.ConnectionError:
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
