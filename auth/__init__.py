from models import *
from forms import *
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user
from extensions import db, mail
from flask_mail import Message
from models.user import update_otp


auth_blp = Blueprint("auth_blp", __name__)


@auth_blp.route("/auth/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for("user_blp.admin"))
    if request.method == "POST":
        email = request.form.get("email").lower()
        if "@" and ".com" not in email:
            flash("A valid Email is required", "danger")
            return redirect(url_for("auth_blp.register"))
        # first_name = request.form.get('first_name').lower()
        username = request.form.get("username").lower()
        # last_name = request.form.get('last_name').lower()
        password = request.form.get("password")
        # confirm_password = request.form.get('confirm_password')

        # Check if any of the required fields (email, password, confirm_password, first_name, last_name, username)
        # are empty
        # required_fields = [email, password, confirm_password, first_name, last_name, username]
        required_fields = [email, password, username]
        if not all(required_fields):
            # Display a flash message to the user indicating that all fields are required
            flash("All fields are required", "danger")
            return render_template(
                "register.html", logged_in=current_user.is_authenticated, form=form
            )

        # if the password and confirm password are not same
        # if password != confirm_password:
        #     flash('Password does\'t match')
        #     return render_template("register.html", logged_in=current_user.is_authenticated, form=form)

        if User.query.filter_by(username=username).first():
            # Username already exists
            flash("Username already exists, please try again.")
            return render_template(
                "register.html", logged_in=current_user.is_authenticated, form=form
            )

        if User.query.filter_by(email=request.form.get("email")).first():
            # User already exists
            flash(
                "You've already signed up with that email, log in instead!", "warning"
            )
            return redirect(url_for("auth_blp.login"))

        hash_and_salted_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        new_user = User(
            email=email,
            # first_name=first_name,
            # last_name=last_name,
            username=username,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        otp = new_user.otp

        msg = Message(
            subject="Email Verification",
            sender="Iszify <iszify.send@gmail.com>",
            recipients=[email],
        )
        msg.html = render_template("email_verification.html", otp=otp)
        mail.send(msg)
        flash("Registration successful, check your email", "success")
        return redirect(url_for("auth_blp.email_verify", email=email))

    return render_template(
        "register.html", logged_in=current_user.is_authenticated, form=form
    )


@auth_blp.route("/auth/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("user_blp.admin"))
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        if not email or not password:
            flash("All inputs are required", "danger")
            return redirect(url_for("auth_blp.login"))

        user_ = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user_:
            flash("That email does not exist, please try again.", "danger")
            return redirect(url_for("auth_blp.login"))
        if not check_password_hash(user_.password, password):
            flash("Password incorrect, please try again.", "danger")
            return redirect(url_for("auth_blp.login"))

        if not user_.email_verified:
            # Email not verified
            otp = user_.otp
            if not otp:
                otp = update_otp(user_)
                msg = Message(
                    subject="Email Verification",
                    sender="Iszify <iszify.send@gmail.com>",
                    recipients=[email],
                )
                msg.html = render_template("email_verification.html", otp=otp)
                mail.send(msg)

            flash("Please verify your email", "danger")
            return redirect(url_for("auth_blp.email_verify", email=email))

        login_user(user_)
        flash("You are now logged in", "success")
        return redirect(url_for("user_blp.dashboard"))

    return render_template(
        "login.html", logged_in=current_user.is_authenticated, form=form
    )


# email verify
@auth_blp.route("/auth/email_verify/<email>", methods=["GET", "POST"])
def email_verify(email):
    if not email:
        return redirect(url_for("auth_blp.login"))
    email = email.lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for("auth_blp.login"))
    if user.email_verified:
        flash("Email already verified, please login", "success")
        return redirect(url_for("auth_blp.login"))
    if request.method == "POST":
        first_input = request.form.get("first")
        second_input = request.form.get("second")
        third_input = request.form.get("third")
        fourth = request.form.get("fourth")
        fifth = request.form.get("fifth")
        sixth = request.form.get("sixth")

        otp = f"{first_input}{second_input}{third_input}{fourth}{fifth}{sixth}"

        if otp != user.otp:
            flash("Invalid OTP", "danger")
            return redirect(url_for("auth_blp.email_verify", email=email))
        user.email_verified = True
        db.session.commit()
        login_user(user)
        flash("Email verified successfully", "success")
        return redirect(url_for("user_blp.dashboard"))
    return render_template("email_verify.html", email=email)


@auth_blp.route("/auth/logout")
def logout():
    logout_user()
    flash("logged out successfully", "success")
    return redirect(url_for("user_blp.home"))


# resend otp
@auth_blp.route("/auth/resend_otp/<email>")
def resend_otp(email):
    if not email:
        return redirect(url_for("auth_blp.email_verify"))
    email = email.lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return redirect(url_for("auth_blp.email_verify"))
    if user.email_verified:
        flash("Email already verified, please login", "success")
        return redirect(url_for("auth_blp.login"))
    otp = update_otp(user)
    msg = Message(
        subject="Email Verification",
        sender="Iszify <iszify.send@gmail.com>",
        recipients=[email],
    )
    msg.html = render_template("email_verification.html", otp=otp)
    mail.send(msg)
    flash("OTP sent successfully", "success")
    return redirect(url_for("auth_blp.email_verify", email=email))
