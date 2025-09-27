from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Database_main.database import db


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:pasle2006@localhost/MovieDB'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app