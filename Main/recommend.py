import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import json


class BookRecommender: 
    def __init__(self):
        # Initialize mappings as class attributes
        self.turnoffs_map = {
            'Predictable plot': {
                'keywords': ['predictable', 'formulaic', 'conventional plot'],
                'genres': ['Romance', 'Contemporary Romance', 'Paranormal Romance'],
                'clusters': [5, 6],
                'min_rating': 0
            },
            'Flat characters': {
                'keywords': ['flat', 'undeveloped characters', 'one-dimensional'],
                'genres': ['Thriller', 'Mystery Thriller', 'Action'],
                'clusters': [2],
                'min_rating': 0
            },
            'Poor writing': {
                'keywords': [],
                'genres': [],
                'clusters': [],
                'min_rating': 4.0
            },
            'Dense writing': {
                'keywords': ['dense', 'academic', 'philosophical'],
                'genres': ['Philosophy', 'Academic', 'Literary Fiction'],
                'clusters': [0, 3],
                'min_rating': 0
            },
            'Shock ending': {
                'keywords': ['twist ending', 'shocking conclusion', 'surprise ending'],
                'genres': ['Thriller', 'Psychological Thriller', 'Horror', 'Mystery'],
                'clusters': [2],
                'min_rating': 0
            },
            'Confusing ending': {
                'keywords': ['ambiguous ending', 'open-ended', 'unclear conclusion'],
                'genres': ['Literary Fiction', 'Experimental', 'Postmodern'],
                'clusters': [3],
                'min_rating': 0
            },
            'Sad ending': {
                'keywords': ['tragic', 'heartbreaking', 'bittersweet'],
                'genres': ['Literary Fiction', 'Historical Fiction', 'War'],
                'clusters': [3],
                'min_rating': 0
            }
        }

        self.characteristic_clusters = {
            'Realistic': [0],
            'World-building': [1, 6],
            'Plot-heavy': [2],
            'Character-driven': [3, 5],
            'Development': [3, 5],
            'Loveable Characters': [4, 5],
            'Quality Writing': [3],
            'Human Experience': [0, 3],
            'Woman Author': [5],
            'Unreliable Characters': [2]
        }

        self.mood_map = {
            'adventurous': [1],
            'dark': [2],
            'lighthearted': [4],
            'emotional': [3],
            'inspiring': [0],
            'mysterious': [2],
            'reflective': [0, 3],
            'tense': [2],
            'hopeful': [0, 4],
            'sad': [3, 5],
            'funny': [4],
            'challenging': [2],
            'informative': [0]
        }
        
        # Load and preprocess books on initialization
        self.books_df, self.vectorizer, self.tfidf_matrix = self._load_and_preprocess_books()
    
    def _load_and_preprocess_books(self):
        """Load and preprocess the books dataset"""
        try:
            books_df = pd.read_csv("Book.csv", encoding='Windows-1254',low_memory=False)
            # Robust genre parsing
            def parse_genres(genre_str):
                if isinstance(genre_str, list):
                    return [g.strip() for g in genre_str if g.strip()]
                
                if isinstance(genre_str, str):
                    try:# Use ast.literal_eval to parse the string
                        parsed_genres = ast.literal_eval(genre_str)
                    # Filter out empty strings and strip whitespace
                        return [g.strip() for g in parsed_genres if g.strip()]
                    except:
                        return [g.strip() for g in genre_str.split(',') if g.strip()]
                return []
            books_df['genres'] = books_df['genres'].apply(parse_genres)
  
            books_df['rating'] = pd.to_numeric(books_df['rating'], errors='coerce')
            books_df['pages'] = pd.to_numeric(books_df['pages'], errors='coerce')
            
            # Fill missing values or drop them if necessary
            books_df['pages'] = books_df['pages'].fillna(0).astype(int)  # Replace NaN with 0 or a default value
            books_df['rating'] = books_df['rating'].fillna(0)    
            books_df['description'] = books_df['description'].fillna("No description available") # Replace NaN with a default valu
            
            def count_awards(awards_str):
                if isinstance(awards_str, list):
                    return len(awards_str) 
                if isinstance(awards_str, str):
                    try:
                        parsed_awards = ast.literal_eval(awards_str) 
                        return len(parsed_awards)
                    except: 
                        return len([a.strip() for a in awards_str.split(',') if a.strip()]) 
                
                return 0 
            
            books_df['awards'] = books_df['awards'].apply(count_awards)
        
        # Create TF-IDF matrix for genre clustering
            genre_docs = [" ".join(genre_list) for genre_list in books_df['genres']]
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(genre_docs)
        
        # Cluster books
            kmeans = KMeans(n_clusters=7, random_state=42)
            books_df['cluster'] = kmeans.fit_predict(tfidf_matrix)
            return books_df, vectorizer, tfidf_matrix
        except Exception as e:
            print(f"Error in _load_and_preprocess_books: {str(e)}")
            raise
    
    def recommend_books(self, user_preferences, num_recommendations=12):
        try:
            # Get survey-based recommendations
            survey_recommendations = self._get_survey_recommendations(user_preferences, num_recommendations)
            
            # Get genre-based recommendations
            genre_recommendations = {}
            if user_preferences.get('favorite_genres'):
                for genre in user_preferences['favorite_genres']:
                    # Create a modified preferences dict focusing on this genre
                    genre_preferences = user_preferences.copy()
                    genre_preferences['favorite_genres'] = [genre]
                    
                    # Get recommendations for this specific genre
                    genre_books = self._get_genre_specific_recommendations(
                        genre_preferences, 
                        num_recommendations=12  # Limit per genre
                    )
                    
                    if not genre_books.empty:
                        genre_recommendations[genre] = genre_books

            return {
                'survey_based': survey_recommendations,
                'genre_based': genre_recommendations
            }
            
        except Exception as e:
            print(f"Error in recommend_books: {str(e)}")
            raise

    def _get_survey_recommendations(self, user_preferences, num_recommendations=12):
        """Get recommendations based on all survey criteria"""
        try:
            filtered_books = self.books_df.copy()
            filtered_books = self._apply_filters(filtered_books, user_preferences)
            
            if filtered_books.empty:
                filtered_books = self._apply_relaxed_filters(self.books_df.copy(), user_preferences)

            if not filtered_books.empty:
                filtered_books = self._calculate_scores(filtered_books, user_preferences)
                return filtered_books.nlargest(num_recommendations, 'final_score')[
                    ['bookId', 'title', 'author', 'genres', 'rating', 'pages', 'awards', 'final_score', 'coverImg','description']
                ].to_dict('records')
            return []
        except Exception as e:
            print(f"Error in _get_survey_recommendations: {str(e)}")
            raise

    def _get_genre_specific_recommendations(self, preferences, num_recommendations):
        """Get recommendations for a specific genre"""
        try:
            filtered_books = self.books_df.copy()
            
            # Apply basic filters
            if preferences.get('min_rating'):
                filtered_books = filtered_books[filtered_books['rating'] >= preferences['min_rating']]
            
            # Filter by genre
            if preferences.get('favorite_genres'):
                genre = preferences['favorite_genres'][0]  # We know there's exactly one genre
                filtered_books = filtered_books[
                    filtered_books['genres'].apply(lambda x: genre in x)
                ]
            
            # Calculate scores
            if not filtered_books.empty:
                filtered_books = self._calculate_scores(filtered_books, preferences)
                return filtered_books.nlargest(num_recommendations, 'final_score')[
                    ['bookId', 'title', 'author', 'genres', 'rating', 'pages', 'awards', 'final_score', 'coverImg','description']
                ]
            return pd.DataFrame()
        except Exception as e:
            print(f"Error in _get_genre_specific_recommendations: {str(e)}")
            raise
    
    def _apply_filters(self, books_df, user_preferences):
        """Apply all filters to the books DataFrame"""
        try:
            # Apply favorite genres filter
            if user_preferences.get('favorite_genres'):
                books_df = books_df[
                    books_df['genres'].apply(
                        lambda x: any(genre in x for genre in user_preferences['favorite_genres'])
                    )
                ]
            
            # Apply characteristic-based filtering
            if user_preferences.get('user_characteristic'):
                relevant_clusters = self.characteristic_clusters.get(user_preferences['user_characteristic'], [0])
                books_df = books_df[books_df['cluster'].isin(relevant_clusters)]
            
            # Apply turnoff-based filtering
            if user_preferences.get('disliked_turnoffs'):
                for turnoff in user_preferences['disliked_turnoffs']:
                    if turnoff == 'Poor writing':
                        books_df = books_df[books_df['rating'] >= 4.0]
                    elif turnoff in self.turnoffs_map:
                        turnoff_info = self.turnoffs_map[turnoff]
                        
                        if turnoff_info['genres']:
                            books_df = books_df[
                                ~books_df['genres'].apply(
                                    lambda x: any(genre in x for genre in turnoff_info['genres'])
                                )
                            ]
                        
                        if turnoff_info['clusters']:
                            books_df = books_df[
                                ~books_df['cluster'].isin(turnoff_info['clusters']) |
                                (books_df['rating'] >= turnoff_info['min_rating'])
                            ]
            
            # Apply other filters
            if user_preferences.get('min_pages'):
                books_df = books_df[books_df['pages'].fillna(0) >= user_preferences['min_pages']]
            
            if user_preferences.get('min_rating'):
                books_df = books_df[books_df['rating'] >= user_preferences['min_rating']]
            
            return books_df
        except Exception as e:
            print(f"Error in _apply_filters: {str(e)}")
            raise

    def _apply_relaxed_filters(self, books_df, user_preferences):
        """Apply relaxed filters when strict filtering yields no results"""
        try:
            if user_preferences.get('search_query'):
                query = user_preferences['search_query'].lower()
                books_df = books_df[
                    books_df['title'].str.lower().str.contains(query, na=False) |
                    books_df['author'].str.lower().str.contains(query, na=False)
                ]

            if user_preferences.get('min_rating'):
                books_df = books_df[books_df['rating'] >= user_preferences['min_rating'] * 0.9]

            if 'Poor writing' in user_preferences.get('disliked_turnoffs', []):
                books_df = books_df[books_df['rating'] >= 4.0]

            return books_df
        except Exception as e:
            print(f"Error in _apply_relaxed_filters: {str(e)}")
            raise

    def _calculate_scores(self, books_df, user_preferences):
        """Calculate final scores for books"""
        try:
            # Award score
            books_df['award_score'] = books_df['awards'].apply(
                lambda x: 1 if isinstance(x, str) and x.strip() != '[]' else 0
            )

            # Initialize similarity score
            books_df['similarity_score'] = 1.0

            # Calculate similarity score if characteristic is provided
            if user_preferences.get('user_characteristic'):
                relevant_clusters = self.characteristic_clusters.get(user_preferences['user_characteristic'], [0])
                user_vector = self.vectorizer.transform([" ".join(map(str, relevant_clusters))])
                cosine_sim = cosine_similarity(user_vector, self.tfidf_matrix[books_df.index])
                books_df['similarity_score'] = cosine_sim[0]

            # Calculate final score
            if 'Poor writing' in user_preferences.get('disliked_turnoffs', []):
                books_df['final_score'] = (
                    books_df['similarity_score'] * 0.3 +
                    books_df['rating'] * 0.5 +
                    books_df['award_score'] * 0.2
                )
            else:
                books_df['final_score'] = (
                    books_df['similarity_score'] * 0.4 +
                    books_df['rating'] * 0.3 +
                    books_df['award_score'] * 0.3
                )
            
            return books_df
        except Exception as e:  
            print(f"Error in _calculate_scores: {str(e)}")
            raise

    def get_available_genres(self):
        """Return list of unique genres from the dataset"""
        all_genres = set()
        for genre_list in self.books_df['genres']:
            all_genres.update(genre_list)
        return sorted(list(all_genres))

    def get_characteristics(self):
        """Return available characteristics"""
        return list(self.characteristic_clusters.keys())

    def get_moods(self):
        """Return available moods"""
        return list(self.mood_map.keys())

    def get_turnoffs(self):
        """Return available turnoffs"""
        return list(self.turnoffs_map.keys())
    
    
    def bookdisp(self):
        
        selected_books = self.books_df.sample(n=min(12, len(self.books_df)))
        finallist = []
        
       
        for _, book in selected_books.iterrows():
            # Add the number of awards to the total
            finallist.append({
                'title': book.get('title', 'Unknown Title'),
                'coverImage': book.get('coverImg', 'Cover Image not available'),
                'author': book.get('author', 'Unknown Author'),
                'pages': book.get('pages') if pd.notna(book.get('pages')) else None,
                'rating': book.get('rating') if pd.notna(book.get('rating')) else None,
                'awards': book.get('awards', []),
                'description': book.get('description', 'No description available')
          
               })
        return finallist
    
    def search_books(self, query, limit=12):
        """Search books by title or author"""
        try:
            query = query.lower()
            filtered_df = self.books_df[
                self.books_df['title'].str.lower().str.contains(query, na=False) |
                self.books_df['author'].str.lower().str.contains(query, na=False)
            ]
            
            # Get up to 'limit' results
            results = filtered_df.head(limit)
            
            search_results = []
            for _, book in results.iterrows():
                
                search_results.append({
                    'title': book.get('title', 'Unknown Title'),
                    'coverImage': book.get('coverImg', ''),
                    'author': book.get('author', 'Unknown Author'),
                    'pages': int(book['pages']) if pd.notna(book.get('pages')) else None,
                    'rating': float(book['rating']) if pd.notna(book.get('rating')) else None,
                    'awards': book.get('awards', []),
                    'description': book.get('description', 'No description available')
                })
            
            return search_results
        except Exception as e:
            print(f"Error in search_books: {str(e)}")
            return []