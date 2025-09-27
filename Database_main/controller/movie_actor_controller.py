from flask import request, jsonify
from Database_main.service.MovieActorService import MovieActorService

movie_actor_service = MovieActorService()


def get_all_movie_actors():
    entries = movie_actor_service.get_all_entries()
    return jsonify([entry.to_dict() for entry in entries]), 200


def get_movie_actor(movie_id, actor_id):
    entry = movie_actor_service.get_entry_by_ids(movie_id, actor_id)
    if entry:
        return jsonify(entry.to_dict()), 200
    return jsonify({'message': 'Entry not found'}), 404

def create_movie_actor():
    try:
        data = request.json
        new_movie_actor = movie_actor_service.add_movie_actor(data)
        return jsonify({
            "message": "Actor added to the movie successfully",
            "movie_actor": new_movie_actor.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        return jsonify({"error": "An unexpected error occurred", "details": traceback.format_exc()}), 500

def update_movie_actor(movie_id, actor_id):
    data = request.json
    updated_entry = movie_actor_service.update_entry(movie_id, actor_id, data)
    if updated_entry:
        return jsonify(updated_entry.to_dict()), 200
    return jsonify({'message': 'Entry not found'}), 404


def delete_movie_actor(movie_id, actor_id):
    success = movie_actor_service.delete_entry(movie_id, actor_id)
    if success:
        return jsonify({'message': 'Entry deleted successfully'}), 200
    return jsonify({'message': 'Entry not found'}), 404

def get_actors_by_movie(movie_id):
    data, error = movie_actor_service.get_actors_by_movie(movie_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200

def get_movies_by_actor(actor_id):
    movies, error = movie_actor_service.get_movies_by_actor(actor_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(movies), 200
