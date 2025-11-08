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

