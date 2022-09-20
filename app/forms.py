from wsgiref.validate import validator
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, Length, Regexp, EqualTo, DataRequired, Optional

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')
    recaptcha = RecaptchaField()

class RegisterForm(FlaskForm):
    first_name = StringField('First Name',
        validators=[Length(min=2, max=15, message="First name must contain between 2 and 15 characters")], 
        render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name',
        validators=[Length(min=2, max=15, message="Last name must contain between 2 and 15 characters")], 
        render_kw={'placeholder': 'Last Name'})
    username = StringField('Username',
        validators=[
            Length(min=2, max=15, message="Username must contain between 2 and 15 characters"), 
            Regexp('^\w+$', message="Username must contain only letters numbers or underscore")], 
        render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', 
        validators=[
            Length(min=8), 
            Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', message="password must contain minimum eight characters, at least one uppercase letter, one lowercase letter and one number:")],
        render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', 
        validators=[EqualTo('password', message="confirm password must be a equal to the password")],
        render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')
    recaptcha = RecaptchaField()
    

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', validators=[Length(min=10, max=300, message="At least 10 characters, maximum 300")], render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', 
        validators=[
            Length(min=1, max=100, message="Comments must cannot be longer than 100 characters, or less than 1 character")],
        render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', 
        validators=[
            Length(min=2, max=15, message="Username must contain between 2 and 15 characters"), 
            Regexp('^\w+$', message="Username must contain only letters numbers or underscore"),],
        render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', 
        validators=[
            Length(max=30, message="Must be less than 30 letters"),
            Regexp('^\w*$', message="Can only contain letters, numbers and underscore")],
        render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', 
        validators=[
            Length(max=30, message="Must be less than 30 letters"),
            Regexp('^\w*$', message="Can only contain letters, numbers and underscore")],
        render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', 
        validators=[
            Length(max=30, message="Must be less than 30 letters"),
            Regexp('^\w*$', message="Can only contain letters, numbers and underscore")],
        render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', 
        validators=[
            Length(max=30, message="Must be less than 30 letters"),
            Regexp('^\w*$', message="Can only contain letters, numbers and underscore")],
        render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', 
        validators=[
            Length(max=30, message="Must be less than 30 letters"),
            Regexp('^\w*$', message="Can only contain letters, numbers and underscore")],
        render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday',
        validators=[Optional()])
    submit = SubmitField('Update Profile')
