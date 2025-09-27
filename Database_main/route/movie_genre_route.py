from flask import Blueprint
from Database_main.controller.movie_genre_controller import (
    get_all_movie_genres,
    add_movie_genre,
    delete_movie_genre
)

movie_genre_bp = Blueprint('movie_genre', __name__)

movie_genre_bp.route('/movie_genres', methods=['GET'])(get_all_movie_genres)
movie_genre_bp.route('/movie_genres', methods=['POST'])(add_movie_genre)
movie_genre_bp.route('/movie_genres/<int:movie_id>/<int:genre_id>', methods=['DELETE'])(delete_movie_genre)
