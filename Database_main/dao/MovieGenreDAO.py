from Database_main.database import db
from Database_main.models.movie_genre import MovieGenre

class MovieGenreDAO:
    def get_all(self):
        return MovieGenre.query.all()
