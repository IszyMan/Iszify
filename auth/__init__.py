from models import *
from forms import *
from flask import Blueprint, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user
from extensions import db


auth_blp = Blueprint("auth_blp", __name__)


@auth_blp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('auth_blp.login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("user_blp.admin"))

    return render_template("register.html", logged_in=current_user.is_authenticated, form=form)


@auth_blp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('All inputs are required', 'danger')
            return redirect(url_for('auth_blp.login'))

        user_ = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user_:
            flash("That email does not exist, please try again.")
            return redirect(url_for('auth_blp.login'))
        elif not check_password_hash(user_.password, password):
            flash('Password incorrect, please try again.', 'danger')
            return redirect(url_for('auth_blp.login'))
        else:
            login_user(user_)
            return redirect(url_for('user_blp.admin'))

    return render_template("login.html", logged_in=current_user.is_authenticated, form=form)


@auth_blp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user_blp.home'))
