from flask import Flask
from Database_main.database import db

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:pasle2006@localhost/moviedb"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from Database_main.models.movie import Movie
        db.create_all()

    return app
