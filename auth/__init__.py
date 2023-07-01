from models import *
from forms import *
from flask import Blueprint, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user
from extensions import db


auth_blp = Blueprint("auth_blp", __name__)


@auth_blp.route('/register/<brandie>/', methods=["GET", "POST"])
def register(brandie):
    form = RegisterForm()
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # if the email or/and password fields are empty
        if not email or not password:
            # flash this message to the user
            flash('All fields are required', 'danger')
            return redirect(url_for('auth_blp.register', brandie=brandie))

        # if the password and confirm password are not same
        if password != confirm_password:
            flash('Password does\'t match')
            return render_template("register.html", logged_in=current_user.is_authenticated, form=form)

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('auth_blp.login'))

        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=email,
            name=name,
            password=hash_and_salted_password,
        )
        new_brand = ChooseBrandName(brandname=brandie)
        db.session.add(new_brand)
        db.session.add(new_user)
        db.session.commit()
        # login_user(new_user)
        flash('Registration successful', 'success')
        return redirect(url_for("auth_blp.login"))

    return render_template("register.html",
                           logged_in=current_user.is_authenticated,
                           form=form, brandie=brandie)


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
    flash('logged out successfully', 'success')
    return redirect(url_for('user_blp.home'))
