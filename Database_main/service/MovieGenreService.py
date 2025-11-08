from Database_main.dao.MovieGenreDAO import MovieGenreDAO



class MovieGenreService:

    def __init__(self):

        self.dao = MovieGenreDAO()



    def get_all_movie_genres(self):

        return [movie_genre.to_dict() for movie_genre in self.dao.get_all()]

