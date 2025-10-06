from Database_main.database import db

class MovieGenre(db.Model):
    __tablename__ = 'movie_genre'

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True)

    def to_dict(self):
        return {
            "movie_id": self.movie_id,
            "genre_id": self.genre_id,
        }
