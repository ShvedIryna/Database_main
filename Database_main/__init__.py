from flask import Flask
from Database_main.database import db

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://CloudSA5110a274:12345iryna_@database-main.database.windows.net:1433/moviedb?driver=ODBC+Driver+17+for+SQL+Server"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from Database_main.models.movie import Movie
        from Database_main.models.actor import Actor
        from Database_main.models.rating import Rating
        from Database_main.models.user import User
        from Database_main.models.genre import Genre
        from Database_main.models.review import Review
        db.create_all()

    return app
