from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL

from flask_ckeditor import CKEditorField
class GenerateBrandName(FlaskForm):
    brandname = StringField("Brand Name", validators=[DataRequired()])
    submit = SubmitField("Create your Brand!")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CreatePostForm(FlaskForm):
    linkname = StringField("Link Name ", validators=[DataRequired()])
    yourlink = StringField("URL", validators=[DataRequired(), URL()])

    # categories = SelectField(u'Category', choices=[("Fashion", 'Fashion'), ("Travel", 'Travel')])

    submit = SubmitField("Add Link")
