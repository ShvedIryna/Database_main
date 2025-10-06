from Database_main.database import db
from Database_main.models.movie import Movie
from Database_main.models.user import User


class Rating(db.Model):
    __tablename__ = 'rating'

    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    movie = db.relationship('Movie', backref=db.backref('ratings', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('ratings', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            "rating_id": self.rating_id,
            "movie_id": self.movie_id,
            "user_id": self.user_id,
            "rating": self.rating,
        }

