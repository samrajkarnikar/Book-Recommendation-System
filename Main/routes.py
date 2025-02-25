from flask import Flask, render_template, url_for, flash, redirect, request
from Main.form import RegistrationForm, LoginForm, BookForm, UploadBook, Contact, DeleteBook, UpdateAccount

from Main.models import User
from flask_sqlalchemy import SQLAlchemy
from Main import app,db,bcrypt
from flask_mail import Message
import secrets
import os
from PIL import Image
import pandas as pd
import numpy as np
from flask_login import login_user, current_user, logout_user, login_required
import csv
from csv import writer
from flask import  request, jsonify, render_template
from Main.recommend import BookRecommender # Your existing BookRecommender class
from flask_cors import CORS
from datetime import datetime
from ast import literal_eval
from functools import wraps
from flask import abort
from flask import jsonify, request, render_template, redirect, url_for
import traceback
import logging

@app.route("/")
@app.route("/home")
def home():
        categories = [
            "Romance",
            "Fantasy", "Science Fiction",
            "Mystery", "Thriller",
            "Horror", "Historical Fiction",
            "Contemporary", "Young Adult",
            "Biography", "Philosophy",
            "Adventure", "Crime", "Drama",
             "War", "Action",
            "Academic"
        ]
        recommender = BookRecommender()
        list1 = recommender.bookdisp()
        return render_template('home.html', categories=categories, content=list1)
    
# routes.py
from flask import jsonify

@app.route("/get_category_books/<category>")
def get_category_books(category):
    try:
        recommender = BookRecommender()
        books_df = recommender.books_df
        
        # Filter books by category
        category_books = books_df[
            books_df['genres'].apply(lambda x: category in x)
        ].sample(n=min(12, len(books_df)))
        
        # Prepare the response
        books_list = []
        for _, book in category_books.iterrows():
            awards = book.get('awards', [])
            total_awards = len(awards) if isinstance(awards, list) else 0
            
            books_list.append({
                'title': book.get('title', 'Unknown Title'),
                'coverImage': book.get('coverImg', ''),
                'author': book.get('author', 'Unknown Author'),
                'pages': int(book['pages']) if pd.notna(book.get('pages')) else None,
                'rating': float(book['rating']) if pd.notna(book.get('rating')) else None,
                'awards': total_awards,
                'description': book.get('description', 'No description available')
            })
        
        return jsonify({'books': books_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/search")
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('home'))
    
    recommender = BookRecommender()
    search_results = recommender.search_books(query)
    return render_template('search_results.html', results=search_results, query=query)

@app.route("/api/search")
def api_search():
    query = request.args.get('q', '')
    recommender = BookRecommender()
    search_results = recommender.search_books(query)
    return jsonify({'results': search_results})

    
@app.route("/about")
def about():
	return render_template('about.html',title="About")



@app.route("/register", methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user=User(username=form.username.data,email=form.email.data,password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account Created for { form.username.data } !', 'success')
		return redirect(url_for('login'))
	return render_template('register.html',title='Register',form=form)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.email != "admin@gmail.com":
            abort(403)  # Forbidden access
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    
    if form.validate_on_submit():
        # Check for admin credentials
        if form.email.data == "admin@gmail.com" and form.password.data == "admin":
            user = User.query.filter_by(email="admin@gmail.com").first()
            if not user:
                # Create admin user if doesn't exist
                hashed_password = bcrypt.generate_password_hash("admin").decode('utf-8')
                user = User(username="admin", email="admin@gmail.com", password=hashed_password)
                db.session.add(user)
                db.session.commit()
            login_user(user, remember=form.remember.data)
            flash('Admin Login Successful!', 'success')
            return redirect(url_for('home'))
        
        # Regular user login
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('User Login Successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


recommender = BookRecommender()

@app.route('/recommend')
@login_required
def recommend():
    """Render the main page"""
    return render_template('recommend.html')


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get book recommendations based on user preferences"""
    try:
        data = request.json
        
        # Transform the input data to match the recommender's expected format
        user_preferences = {
            'favorite_genres': data.get('favoriteGenres', []),
            'unwanted_genres': data.get('dislikedGenres', []),
            'user_characteristic': next(iter(data.get('characteristics', [])), None),
            'disliked_turnoffs': data.get('turnoffs', []),
            'unwanted_mood': next(iter(data.get('moods', [])), None),
            'min_pages': int(data.get('bookLength', 0)) if data.get('bookLength') and str(data.get('bookLength')).isdigit() else None,
            'min_rating': float(data.get('minRating', 0)) if data.get('minRating') and isinstance(data.get('minRating'), (int, float, str)) else None,
            'search_query': data.get('searchQuery', ''),
        }
        # Ensure no NaN values 
        user_preferences = {k: (0 if v is None else v) for k, v in user_preferences.items()} 
        
        # Get recommendations 
        all_recommendations = recommender.recommend_books(user_preferences)
        # Get recommendations
        #all_recommendations = recommender.recommend_books(user_preferences)
        
        # Process survey-based recommendations
        survey_recs = [
            {
                'title': book['title'],
                'author': book['author'],
                'pages': book['pages'],
                'rating': book['rating'],
                'genres': literal_eval(book['genres']) if isinstance(book['genres'], str) else book['genres'],
                'coverImage':'' if pd.isna(book.get('coverImg')) else book.get('coverImg', ''),
                'awards': book['awards'],
                'description': book['description'] }
            for book in all_recommendations['survey_based']
        ]
        
        # Process genre-based recommendations
        genre_recs = {}
        for genre, books_df in all_recommendations['genre_based'].items():
            genre_recs[genre] = [
                {
                    'title': book['title'],
                    'author': book['author'],
                    'pages': book['pages'],
                    'rating': book['rating'],
                    'genres': literal_eval(book['genres']) if isinstance(book['genres'], str) else book['genres'],
                    'coverImage': '' if pd.isna(book.get('coverImg')) else book.get('coverImg', ''),
                    'awards': book['awards'],
                    'description': book['description']
                }
                for book in books_df.to_dict('records')
            ]
        
        return jsonify({
            'success': True,
            'recommendations': {
                'survey_based': survey_recs,
                'genre_based': genre_recs
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_recommendations: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

           
@app.route("/uploadbook",methods=['GET','POST'])
@login_required
@admin_required

def uploadbook():
    form = UploadBook()
    
    # Debugging print statements
    if request.method == 'POST':
        print("POST data received")
        print("Form data:", request.form)
        
        # Check form validation
        if form.validate_on_submit():
            try:
                # Ensure the CSV file exists
                csv_path = 'Book.csv'
               
                if not os.path.exists(csv_path):
                    # Create the file with headers if it doesn't exist
                    df = pd.DataFrame(columns=[
                        'bookId', 'title', 'series', 'author', 'rating', 
                        'description', 'language', 'isbn', 'genres', 
                        'characters', 'bookFormat', 'edition', 'pages', 
                        'publisher', 'publishDate', 'firstPublishDate', 
                        'awards', 'numRatings', 'ratingsByStars', 
                        'likedPercent', 'setting', 'coverImg', 
                        'bbeScore', 'bbeVotes', 'price'
                    ])
                    df.to_csv(csv_path, index=False, encoding='Windows-1254')
                
                # Read existing data
                df = pd.read_csv(csv_path, encoding='Windows-1254')
                
                # Prepare new book data
                new_book = {
                    'bookId': form.bookId.data,
                    'title': form.title.data,
                    'series': form.series.data,
                    'author': form.author.data,
                    'rating': form.rating.data,
                    'description': form.description.data,
                    'language': form.language.data,
                    'isbn': form.isbn.data,
                    'genres': form.genres.data,
                    'characters': form.characters.data,
                    'bookFormat': form.bookFormat.data,
                    'edition': form.edition.data,
                    'pages': form.pages.data,
                    'publisher': form.publisher.data,
                    'publishDate': form.publishDate.data,
                    'firstPublishDate': form.firstPublishDate.data,
                    'awards': form.awards.data,
                    'numRatings': form.numRatings.data,
                    'ratingsByStars': form.ratingsByStars.data,
                    'likedPercent': form.likedPercent.data,
                    'setting': form.setting.data,
                    'coverImg': form.coverImg.data,
                    'bbeScore': form.bbeScore.data,
                    'bbeVotes': form.bbeVotes.data,
                    'price': form.price.data
                }
                
                # Add new book to DataFrame
                df = pd.concat([df, pd.DataFrame([new_book])], ignore_index=True)
                
                # Save to CSV
                df.to_csv('Book.csv', index=False, encoding='Windows-1254')
                
                print("Book uploaded successfully")
                flash('Book Uploaded Successfully', 'success')
                return redirect(url_for('home'))
            
            except Exception as e:
                print(f"Error uploading book: {e}")
                flash(f'Error uploading book: {e}', 'error')
        else:
            print("Form validation failed")
            print("Form errors:", form.errors)
            
    return render_template('uploadbook.html', title='Upload Book', form=form)

@app.route("/contact",methods=['GET','POST'])
@login_required
def contact():
	form=Contact()
	cur=current_user.username
	return render_template('contact.html',title='Contact',current=cur,form=form)

@app.route('/api/results', methods=['GET'])
def results():
    # Pass any data the results page needs
    return render_template('result.html', recommendations={})


@app.route("/deletebook", methods=['GET', 'POST'])
@login_required
@admin_required
def deletebook():
    form = DeleteBook()
    if form.validate_on_submit():
        isbn = form.isbn.data
        print(f"Attempting to delete book with ISBN: {isbn}")
        
        # Check if file exists
        if not os.path.exists('Book.csv'):
            flash('Book database file not found', 'error')
            return redirect(url_for('home'))
            
        success = delete_book(isbn, 'Book.csv')
        if success:
            flash('Book Deleted Successfully', 'success')
        else:
            flash('Book not found or error occurred during deletion', 'error')
        return redirect(url_for('home'))
    
    return render_template('deletebook.html', title='Delete Book', form=form)

def delete_book(isbn_num, file_name):
    try:
        # Load the CSV file
        if not os.path.exists(file_name):
            print("File not found")
            return False

        df = pd.read_csv(file_name, encoding='Windows-1254')

        # Ensure ISBN column is string for consistent comparison
        df['isbn'] = df['isbn'].astype(str)
        isbn_num = str(isbn_num)
        
        # Debugging: Check if ISBN exists
        if isbn_num not in df['isbn'].values:
            print(f"ISBN {isbn_num} not found in the file")
            return False

        # Remove the book and update the file
        df = df[df['isbn'] != isbn_num]
        df.to_csv(file_name, index=False, encoding='Windows-1254')

        print(f"Successfully deleted book with ISBN {isbn_num}")
        return True

    except Exception as e:
        print(f"Error deleting book: {e}")
        return False


@app.route("/logout")
def logout():
	logout_user()
	flash(f'You have been logged out successfully !','success')
	return redirect(url_for('home'))


def save_picture(form_picture):
	random_hex=secrets.token_hex(8)
	f_name, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path=os.path.join(app.root_path,'static/profile_pics',picture_fn)

	op_size=(125,125)
	i=Image.open(form_picture)
	i.thumbnail(op_size)
	i.save(picture_path)

	return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccount()
	if form.validate_on_submit():
		if form.picture.data:
			pic_file=save_picture(form.picture.data)
			current_user.image_file=pic_file
		current_user.username=form.username.data
		current_user.email=form.email.data
		db.session.commit()
		flash('Your account has been updated','success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data=current_user.username
		form.email.data=current_user.email
	image_file=url_for('static', filename='profile_pics/'+current_user.image_file)
	return render_template('account.html', title='Account',image_file=image_file, form = form)