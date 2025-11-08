from flask import request, jsonify

from Database_main.service.MovieGenreService import MovieGenreService



movie_genre_service = MovieGenreService()



def get_all_movie_genres():

    movie_genres = movie_genre_service.get_all_movie_genres()

    return jsonify(movie_genres), 200

