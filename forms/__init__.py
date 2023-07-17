from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, EqualTo
from wtforms.widgets import TextInput


# class PlaceholderInput(TextInput):
#     def __call__(self, field, **kwargs):
#         if 'placeholder' not in kwargs:
#             kwargs['placeholder'] = field.label.text
#         return super(PlaceholderInput, self).__call__(field, **kwargs)


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
    product = StringField("Product", validators=[DataRequired()], render_kw={"placeholder": "Product"})
    linkname = StringField("Link Name ", validators=[DataRequired()], render_kw={"placeholder": "Link name"})
    twitter_link = StringField("Twitter Url", validators=[DataRequired(), URL()], render_kw={"placeholder": "Twitter link"})
    facebook_link = StringField("Facebook Url", validators=[DataRequired(), URL()], render_kw={"placeholder": "Facebook link"})
    amazon_link = StringField("Amazon Url", validators=[DataRequired(), URL()], render_kw={"placeholder": "Amazon link"})
    youtube_link = StringField("Youtube Url", validators=[DataRequired(), URL()], render_kw={"placeholder": "Youtube link"})

    # categories = SelectField(u'Category', choices=[("Fashion", 'Fashion'), ("Travel", 'Travel')])

    submit = SubmitField("Add Link")
