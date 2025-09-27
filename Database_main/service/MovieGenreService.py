from Database_main.dao.Movie_GenreDAO import MovieGenreDAO

class MovieGenreService:
    def __init__(self):
        self.dao = MovieGenreDAO()

    def get_all_movie_genres(self):
        return [movie_genre.to_dict() for movie_genre in self.dao.get_all()]

    def add_movie_genre(self, data):
        return self.dao.create(data).to_dict()

    def delete_movie_genre(self, movie_id, genre_id):
        return self.dao.delete(movie_id, genre_id)
