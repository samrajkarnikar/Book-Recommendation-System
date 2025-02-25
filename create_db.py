from Main import app, db
from Main.models import User  # Ensure you're importing the User model

with app.app_context():
    db.create_all()
