from sqlalchemy.exc import SQLAlchemyError
from Database_main.database import db
from sqlalchemy.sql import text
from Database_main.models.rating import Rating
from Database_main.models.user import User


class RatingDAO:
    def get_all(self):
        return Rating.query.all()

    def get_by_id(self, rating_id):
        return Rating.query.get(rating_id)

    def create_rating(self, movie_id, rating, user_id):
        new_rating = Rating(movie_id=movie_id, rating=rating, user_id=user_id)
        self.session.add(new_rating)
        self.session.commit()
        return new_rating

    def update(self, rating_id, data):
        rating = Rating.query.get(rating_id)
        if rating:
            for key, value in data.items():
                setattr(rating, key, value)
            db.session.commit()
            return rating
        return None

    def delete(self, rating_id):
        try:
            rating = Rating.query.get(rating_id)
            if not rating:
                return None

            db.session.delete(rating)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def get_ratings_by_movie(self, movie_id):
        return Rating.query.filter(Rating.movie_id == movie_id).all()

    def update_with_log(self, rating_id, new_rating):
        try:
            rating = Rating.query.get(rating_id)
            if not rating:
                return None

            old_rating = rating.rating
            rating.rating = new_rating

            log_entry = RatingLog(
                rating_id=rating.rating_id,
                old_rating=old_rating,
                new_rating=new_rating
            )
            db.session.add(log_entry)
            db.session.commit()
            return rating
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    def get_ratings_by_user(self, user_id):
        from my_project.auth.models.rating import Rating
        return Rating.query.filter_by(user_id=user_id).first()

    def get_stat(self, operation):
        try:
            conn = db.session.connection()

            conn.execute(text("CALL GetRatingStat(:operation, @result)"), {'operation': operation})
            result = conn.execute(text("SELECT @result AS result")).fetchone()

            return result[0] if result else None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e
