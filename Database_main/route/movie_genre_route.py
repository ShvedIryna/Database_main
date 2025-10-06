from flask import Blueprint
from Database_main.controller.movie_genre_controller import (get_all_movie_genres)

movie_genre_bp = Blueprint('movie_genre', __name__)

movie_genre_bp.route('/movie_genres', methods=['GET'])(get_all_movie_genres)
