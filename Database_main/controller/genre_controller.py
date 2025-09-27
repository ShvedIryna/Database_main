from flask import request, jsonify
from Database_main.service.GenreService import GenreService

genre_service = GenreService()

def get_all_genres():
    genres = genre_service.get_all_genres()
    return jsonify(genres), 200

def get_genre_by_id(genre_id):
    genre = genre_service.get_genre_by_id(genre_id)
    if genre:
        return jsonify(genre), 200
    return jsonify({'message': 'Genre not found'}), 404

def create_genre():
    data = request.json
    new_genre = genre_service.create_genre(data)
    return jsonify(new_genre), 201

def update_genre(genre_id):
    data = request.json
    updated_genre = genre_service.update_genre(genre_id, data)
    if updated_genre:
        return jsonify(updated_genre), 200
    return jsonify({'message': 'Genre not found'}), 404

def delete_genre(genre_id):
    success = genre_service.delete_genre(genre_id)
    if success:
        return jsonify({'message': 'Genre deleted successfully'}), 200
    return jsonify({'message': 'Genre not found'}), 404
