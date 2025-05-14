from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class ProjectForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание проекта')
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    attachment = FileField('Attachment')
    submit = SubmitField('Create / Update Task')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


