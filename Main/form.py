from typing import Optional
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import SelectMultipleField, StringField, PasswordField, SubmitField, BooleanField, FloatField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length,Email,EqualTo, ValidationError,Optional
from Main.models import User



class RegistrationForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password',validators=[DataRequired()])
	confirm_pswd=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField('Sign Up')

	def validate_username(self,username):
		user=User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please Choose a different one.')

	def validate_email(self,email):
		user=User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please Choose a different one.')



class LoginForm(FlaskForm):
	email=StringField('Email',validators=[DataRequired(),Email()])
	password=PasswordField('Password',validators=[DataRequired()])
	remember=BooleanField('Remember Me')
	submit=SubmitField('Login')

class BookForm(FlaskForm):
	bookname=StringField('Enter Book Name',validators=[DataRequired()])
	submit=SubmitField('Get Recommendations !')
 
class UploadBook(FlaskForm):
    bookId = IntegerField('Book ID', validators=[
        DataRequired(message="Book ID is required")
    ]) 
    title = StringField('Title', validators=[
        DataRequired(message="Title is required")
    ]) 
    series = StringField('Series', validators=[Optional()]) 
    author = StringField('Author', validators=[
        DataRequired(message="Author name is required")
    ]) 
    rating = FloatField('Rating', validators=[Optional()]) 
    description = TextAreaField('Description', validators=[Optional()]) 
    language = StringField('Language', validators=[Optional()]) 
    isbn = StringField('ISBN', validators=[
        DataRequired(message="ISBN is required"),
        Length(min=10, max=13, message="ISBN must be between 10 and 13 characters")
    ]) 
    genres = SelectMultipleField('Genres', choices=[ 
                                                    ('Romance', 'Romance'), 
                                                    ('Contemporary Romance', 'Contemporary Romance'), 
                                                    ('Paranormal Romance', 'Paranormal Romance'), 
                                                    ('Fantasy', 'Fantasy'), 
                                                    ('Science Fiction', 'Science Fiction'), 
                                                    ('Mystery', 'Mystery'), 
                                                    ('Thriller', 'Thriller'), 
                                                    ('Mystery Thriller', 'Mystery Thriller'), 
                                                    ('Horror', 'Horror'), 
                                                    ('Historical Fiction', 'Historical Fiction'), 
                                                    ('Literary Fiction', 'Literary Fiction'), 
                                                    ('Contemporary', 'Contemporary'), 
                                                    ('Young Adult', 'Young Adult'), 
                                                    ('Non-Fiction', 'Non-Fiction'), 
                                                    ('Biography', 'Biography'), 
                                                    ('Philosophy', 'Philosophy'), 
                                                    ('Classic', 'Classic'), 
                                                    ('Adventure', 'Adventure'), 
                                                    ('Crime', 'Crime'), 
                                                    ('Drama', 'Drama'), 
                                                    ('Dystopian', 'Dystopian'), 
                                                    ('War', 'War'), 
                                                    ('Action', 'Action'), 
                                                    ('Academic', 'Academic'), 
                                                    ('Experimental', 'Experimental'), 
                                                    ('Postmodern', 'Postmodern') 
                                                    ],validators=[DataRequired(message="At least one genre is required")
    ]) 
    characters = StringField('Characters', validators=[Optional()]) 
    bookFormat = StringField('Book Format', validators=[Optional()]) 
    edition = StringField('Edition', validators=[Optional()]) 
    pages = IntegerField('Pages', validators=[
        DataRequired(message="Number of pages is required")
    ]) 
    publisher = StringField('Publisher', validators=[Optional()]) 
    publishDate = StringField('Publish Date', validators=[Optional()]) 
    firstPublishDate = StringField('First Publish Date', validators=[Optional()]) 
    awards = StringField('Awards', validators=[Optional()])
    numRatings = IntegerField('Number of Ratings', validators=[Optional()]) 
    ratingsByStars = StringField('Ratings by Stars', validators=[Optional()]) 
    likedPercent = FloatField('Liked Percent', validators=[Optional()]) 
    setting = StringField('Setting', validators=[Optional()]) 
    coverImg = StringField('Cover Image URL', validators=[Optional()]) 
    bbeScore = FloatField('BBE Score', validators=[Optional()]) 
    bbeVotes = IntegerField('BBE Votes', validators=[Optional()]) 
    price = FloatField('Price', validators=[Optional()])
     
    submit = SubmitField('Upload Details')

class Contact(FlaskForm):
	subject=StringField('Subject',validators=[DataRequired(),Length(min=5,max=12)])
	query=StringField('Query',validators=[DataRequired()])
	submit=SubmitField('Submit')

class DeleteBook(FlaskForm): 
    isbn = StringField('Enter ISBN:', validators=[DataRequired(), Length(min=10, max=13)]) 
    submit = SubmitField('Delete Book')


class UpdateAccount(FlaskForm):
	username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
	email=StringField('Email',validators=[DataRequired(),Email()])
	picture=FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
	submit=SubmitField('Update')

	def validate_username(self,username):
		if username.data != current_user.username:
			user=User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please Choose a different one.')

	def validate_email(self,email):
		if email.data != current_user.email:
			user=User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please Choose a different one.')

