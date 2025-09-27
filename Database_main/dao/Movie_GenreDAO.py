from Database_main.database import db
from Database_main.models.movie_genre import MovieGenre

class MovieGenreDAO:
    def get_all(self):
        return MovieGenre.query.all()

    def create(self, data):
        new_entry = MovieGenre(**data)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    def delete(self, movie_id, genre_id):
        entry = MovieGenre.query.filter_by(movie_id=movie_id, genre_id=genre_id).first()
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False
