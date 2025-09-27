from flask import Blueprint
from Database_main.controller.movie_actor_controller import (
    get_all_movie_actors, get_movie_actor, create_movie_actor, update_movie_actor, delete_movie_actor,get_actors_by_movie,
get_movies_by_actor
)

movie_actor_bp = Blueprint('movie_actor', __name__)

movie_actor_bp.route('/movie-actors', methods=['GET'])(get_all_movie_actors)
movie_actor_bp.route('/movie-actors/<int:movie_id>/<int:actor_id>', methods=['GET'])(get_movie_actor)
movie_actor_bp.route('/movie-actors', methods=['POST'])(create_movie_actor)
movie_actor_bp.route('/movie-actors/<int:movie_id>/<int:actor_id>', methods=['PUT'])(update_movie_actor)
movie_actor_bp.route('/movie-actors/<int:movie_id>/<int:actor_id>', methods=['DELETE'])(delete_movie_actor)
movie_actor_bp.route('/movie-actors/<int:movie_id>', methods=['GET'])(get_actors_by_movie)
movie_actor_bp.route('/movie-actors/<int:actor_id>/movies', methods=['GET'])(get_movies_by_actor)