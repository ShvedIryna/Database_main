from flask import abort
from Database_main.dao.ReviewDAO import ReviewDAO

class ReviewService:
    def __init__(self):
        self.review_dao = ReviewDAO()

    def get_all_reviews(self):
        return self.review_dao.get_all()

    def get_review_by_id(self, review_id):
        return self.review_dao.get_by_id(review_id)

    def create_review(self, data):
        movie_id = data.get('movie_id')
        review_text = data.get('review_text')
        review_date = data.get('review_date')
        user_name = data.get('user_name')

        if not movie_id or not review_text or not review_date or not user_name:
            abort(400, description="All fields (movie_id, review_text, review_date, user_name) are required.")

        new_review = self.review_dao.create_review(movie_id, review_text, review_date, user_name)

        return new_review

    def delete_review(self, review_id):
        return self.review_dao.delete(review_id)

    def get_reviews_by_movie(self, movie_id):
        reviews = self.review_dao.get_reviews_by_movie(movie_id)
        if not reviews:
            return None, 'No reviews found for this movie'
        return [review.to_dict() for review in reviews], None
