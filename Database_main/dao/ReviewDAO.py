from Database_main.database import db
from Database_main.models.review import Review

class ReviewDAO:
    def get_all(self):
        return Review.query.all()

    def get_by_id(self, review_id):
        return Review.query.get(review_id)

    def create_review(self, movie_id, review_text, review_date, user_name):
        new_review = Review(
            movie_id=movie_id,
            review_text=review_text,
            review_date=review_date,
            user_name=user_name
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review

    def delete(self, review_id):
        review = Review.query.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()
            return True
        return False

    def get_reviews_by_movie(self, movie_id):
        return Review.query.filter(Review.movie_id == movie_id).all()
