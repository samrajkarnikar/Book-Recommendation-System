# Book Recommendation System
 Content Based Filtering Using K-Means Clustering Algorithm
====================================
 Book recommendation system using Python that applies machine learning techniques to provide personalized suggestions. 

1.Engineered a complete ETL pipeline using pandas for data cleaning, transformation, and preprocessing of book metadata
2.Implemented advanced text analysis with scikit-learn's TF-IDF vectorizer to capture semantic similarities between books
3.Applied K-means clustering to categorize books into distinct reader preference groups
4.Designed and built a multi-criteria filtering system accounting for user-specific preferences including genre, writing style, content preferences, and quality thresholds
5.Created weighted scoring algorithms that balance multiple factors like reader ratings, literary awards, and similarity measures
6.Developed search functionality with intelligent relaxation of constraints to always provide relevant recommendations
7.Built a system robust against missing or malformed data through comprehensive error handling and data validation

#
============================================
### (a) Create a Virtual Environment in Anaconda
1. Open **Anaconda Prompt**.
2. Create a new virtual environment:
   ```
   conda create --name myenv python=3.10
   ```
   Replace `myenv` with your preferred name.
3. Activate the virtual environment:
   - **Windows:**
     ```
     conda activate myenv
     ```
   - **Mac/Linux:**
     ```
     source activate myenv
     ```
#
======================================
### (b) Run the Virtual Environment in Visual Studio Code
1. Open **VS Code**.
2. Install the **Python Extension** if not installed.
3. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette.
4. Search for and select **"Python: Select Interpreter"**.
5. Choose the virtual environment path:
   - **Windows:** `C:\Users\YourUser\anaconda3\envs\myenv\python.exe`
   - **Mac/Linux:** `~/anaconda3/envs/myenv/bin/python`
6. Open a new terminal in VS Code and activate the virtual environment:
   - **Windows:** `conda activate myenv`
   - **Mac/Linux:** `source activate myenv`
#
====================================

### (c) Create a Database in SQLite Using `create_db.py`
1. Open your project folder in VS Code.
2. Create a new Python script named `create_db.py`.
3. Run the script:
   ```
   python create_db.py
   ```
   This creates `books.db` in your project directory.
** Database file is stored in instance **

#
====================================

### (d) Extensions to See SQLite Database and Jupyter Notebook
1. **For SQLite Database:**
   - Install the **SQLite Viewer** extension in VS Code.
   - Open the database file (`books.db`) using the extension to browse tables and run queries.

2. **For Jupyter Notebook:**
   - Install the **Jupyter** extension in VS Code.
   - Ensure Jupyter is installed in the virtual environment:
     ```
     pip install jupyter
     ```
   - Create a new `.ipynb` file and open it in VS Code.

#
====================================

### (e) Run `requirements.txt` and `run.py`
1. Install dependencies from `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```
2. Run `run.py` or click on the play button(upper right side) after opening run.py:
   ```
   python run.py
   ```

#
====================================

### (f) Definitions of Common Project Files
1. **`templates/`** - Contains HTML files for the frontend (Jinja templates in Flask).
2. **`static/`** - Contains static files like CSS, JavaScript, and images.
3. **`routes.py`** - Handles URL routing and connects functions to endpoints in a Flask app.
4. **`form.py`** - Defines classes for user input forms using Flask-WTF.
5. **`recommend.py`** - Implements the book recommendation logic based on user preferences.

#
====================================

### Output



https://github.com/user-attachments/assets/acf8b89f-badd-4446-81b1-0f06f1dd318f


