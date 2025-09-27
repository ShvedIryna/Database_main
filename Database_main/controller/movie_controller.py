from flask import request, jsonify
from Database_main.service.MovieService import MovieService

movie_service = MovieService()


def get_all_movies():
    movies = movie_service.get_all_movies()
    return jsonify([movie.to_dict() for movie in movies]), 200


def get_movie_by_id(movie_id):
    movie = movie_service.get_movie_by_id(movie_id)
    if movie:
        return jsonify(movie.to_dict()), 200
    return jsonify({'message': 'Movie not found'}), 404


def create_movie():
    data = request.json
    new_movie = movie_service.create_movie(data)
    return jsonify(new_movie.to_dict()), 201


def update_movie(movie_id):
    data = request.json
    updated_movie = movie_service.update_movie(movie_id, data)
    if updated_movie:
        return jsonify(updated_movie.to_dict()), 200
    return jsonify({'message': 'Movie not found'}), 404


def delete_movie(movie_id):
    success = movie_service.delete_movie(movie_id)
    if success:
        return jsonify({'message': 'Movie deleted successfully'}), 200
    return jsonify({'message': 'Movie not found'}), 404
