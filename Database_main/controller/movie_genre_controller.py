from flask import request, jsonify
from Database_main.service.MovieGenreService import MovieGenreService

movie_genre_service = MovieGenreService()

def get_all_movie_genres():
    movie_genres = movie_genre_service.get_all_movie_genres()
    return jsonify(movie_genres), 200

def add_movie_genre():
    data = request.json
    new_movie_genre = movie_genre_service.add_movie_genre(data)
    return jsonify(new_movie_genre), 201

def delete_movie_genre(movie_id, genre_id):
    success = movie_genre_service.delete_movie_genre(movie_id, genre_id)
    if success:
        return jsonify({'message': 'MovieGenre entry deleted successfully'}), 200
    return jsonify({'message': 'MovieGenre entry not found'}), 404
