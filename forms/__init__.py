from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, validators
from wtforms.validators import DataRequired, URL, Email, EqualTo
from wtforms.widgets import TextInput


# class PlaceholderInput(TextInput):
#     def __call__(self, field, **kwargs):
#         if 'placeholder' not in kwargs:
#             kwargs['placeholder'] = field.label.text
#         return super(PlaceholderInput, self).__call__(field, **kwargs)


class GenerateBrandName(FlaskForm):
    domainname = SelectField(u'Select Domain name ▽', choices=[('iszzly', 'iszz.ly'), ('iszzto', 'iszz.to'), ('iszzit', 'iszz.it')])
    brandname = StringField("Bio Name", validators=[DataRequired()])

    submit = SubmitField("Create your Bio!")


class RegisterForm(FlaskForm):
    # first_name = StringField("First Name", validators=[DataRequired()])
    # last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField(
        "User Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "User Name", "class": "form-control"},
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            validators.Email("This field requires a valid email " "address"),
        ],
        render_kw={"placeholder": "Email", "class": "form-control"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Password", "class": "form-control"},
    )
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Me Up!", render_kw={"id": "btn-block"})


class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(), validators.Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CreatePostForm(FlaskForm):
    linkname = StringField(
        "Link Name ",
        validators=[DataRequired()],
        render_kw={"placeholder": "Link name"},
    )
    link = StringField(
        "Twitter Url",
        validators=[DataRequired(), URL()],
        render_kw={"placeholder": "Enter your link URL"},
    )

    # categories = SelectField(u'Category', choices=[("Fashion", 'Fashion'), ("Travel", 'Travel')])

    submit = SubmitField("Add Link")
