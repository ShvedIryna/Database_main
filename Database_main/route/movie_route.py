from flask import Blueprint
from Database_main.controller.movie_controller import (
    get_all_movies, get_movie_by_id, create_movie, update_movie, delete_movie
)

movie_bp = Blueprint('movie', __name__)

movie_bp.route('/movies', methods=['GET'])(get_all_movies)
movie_bp.route('/movies/<int:movie_id>', methods=['GET'])(get_movie_by_id)
movie_bp.route('/movies', methods=['POST'])(create_movie)
movie_bp.route('/movies/<int:movie_id>', methods=['PUT'])(update_movie)
movie_bp.route('/movies/<int:movie_id>', methods=['DELETE'])(delete_movie)
