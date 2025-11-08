import json
import flask.json as flask_json_module

if not hasattr(flask_json_module, 'JSONEncoder'):
    flask_json_module.JSONEncoder = json.JSONEncoder

from flask import Flask
from Database_main.database import db
import os
from urllib.parse import quote_plus
from sqlalchemy.exc import OperationalError

def create_app():
    app = Flask(__name__)

    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password')
    DB_NAME = os.environ.get('DB_NAME', 'MovieDB')

    encoded_password = quote_plus(DB_PASSWORD)
    encoded_user = quote_plus(DB_USER)

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{encoded_user}:{encoded_password}@{DB_HOST}:3306/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {
            'ssl': {
                'ca': None,
                'check_hostname': False
            }
        }
    }

    db.init_app(app)

    with app.app_context():
        from Database_main.models.movie import Movie
        from Database_main.models.actor import Actor
        from Database_main.models.rating import Rating
        from Database_main.models.user import User
        from Database_main.models.genre import Genre
        from Database_main.models.review import Review
        try:
            db.create_all()
        except OperationalError as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "1050" in error_str:
                pass
            else:
                raise
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "1050" in error_str:
                pass
            else:
                raise
    return app
