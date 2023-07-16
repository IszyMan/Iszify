from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, EqualTo


class GenerateBrandName(FlaskForm):
    brandname = StringField("Brand Name", validators=[DataRequired()])
    submit = SubmitField("Create your Brand!")


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("User Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CreatePostForm(FlaskForm):
    product = StringField("Product", validators=[DataRequired()])
    linkname = StringField("Link Name ", validators=[DataRequired()])
    twitter_link = StringField("Twitter Url", validators=[DataRequired(), URL()])
    facebook_link = StringField("Facebook Url", validators=[DataRequired(), URL()])
    amazon_link = StringField("Amazon Url", validators=[DataRequired(), URL()])
    youtube_link = StringField("Youtube Url", validators=[DataRequired(), URL()])

    # categories = SelectField(u'Category', choices=[("Fashion", 'Fashion'), ("Travel", 'Travel')])

    submit = SubmitField("Add Link")
