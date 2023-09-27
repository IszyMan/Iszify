from flask import Blueprint, render_template, redirect, url_for, request, flash
from forms import *
from models import *
from extensions import db

unauth_user_blp = Blueprint("user_blp", __name__)


@unauth_user_blp.route("/short-my-url", methods=["GET", "POST"])
def short_my_url():
    if request.method == 'POST':
        long_url = request.form['long_url']