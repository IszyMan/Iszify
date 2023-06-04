from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, CreatePostForm, GenerateBrandName
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditor

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CREATE TABLE IN DB
class ChooseBrandName(UserMixin, db.Model):
    __tablename__ = "brand_name"
    id = db.Column(db.Integer, primary_key=True)
    brandname = db.Column(db.String(100), unique=True)
    brand = relationship("User", back_populates="brand")



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brand_name.brandname"))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    brand = relationship("ChooseBrandName", back_populates="brand")
    posts = relationship("CreateProfile", back_populates="author")



class CreateProfile(UserMixin, db.Model):
    __tablename__ = "users_links"
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.Integer, db.ForeignKey("users.name"))
    author = relationship("User", back_populates="posts")
    linkname = db.Column(db.String(250), nullable=False)
    yourlink = db.Column(db.String(250), nullable=False)



#Line below only required once, when creating DB.
db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    posts = CreateProfile.query.all()
    return render_template("index.html", all_posts=posts)



@app.route('/join', methods=["GET", "POST"])
def join():
    # Every render_template has a logged_in variable set.
    form = GenerateBrandName()
    if request.method == "POST":

        user = ChooseBrandName.query.filter_by(brandname=request.form.get('brandname')).first()
        if user:
            # User already exists
            flash("Brand Name already exists!")
            return redirect(url_for('home'))

        new_user = ChooseBrandName(
            brandname=request.form.get('brandname'),

        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("register"))

    return render_template("join.html", form=form, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

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
        return redirect(url_for("admin"))

    return render_template("register.html", logged_in=current_user.is_authenticated, form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('admin'))

    return render_template("login.html", logged_in=current_user.is_authenticated, form=form)


@app.route('/admin', methods=["GET", "POST"])
@login_required
def admin():
    form = CreatePostForm()
    posts = CreateProfile.query.all()
    if form.validate_on_submit():
        new_post = CreateProfile(
            linkname=form.linkname.data,
            yourlink=form.yourlink.data,
            author=current_user

        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("admin.html", all_posts=posts, name=current_user.name, logged_in=True, form=form)

@app.route('/<path:sub_path>', methods=["GET", "POST"])
def profile(sub_path):
    requested_profile = None
    all_profiles = User.query.all()
    for profiles in all_profiles:
        if profiles.name == sub_path:
            requested_profile = profiles
    return render_template("profile.html",  all_posts=requested_profile, current_user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))





if __name__ == "__main__":
    app.run(debug=True)
