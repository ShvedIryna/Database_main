from Database_main.dao.RatingDAO import RatingDAO

from sqlalchemy.exc import SQLAlchemyError





class RatingService:

    def __init__(self):

        self.rating_dao = RatingDAO()



    def get_all_ratings(self):

        return self.rating_dao.get_all()



    def get_rating_by_id(self, rating_id):

        return self.rating_dao.get_by_id(rating_id)



    def create_rating(self, movie_id, rating, user_id):

        if not (1 <= rating <= 10):

            raise ValueError("Rating must be between 1 and 10.")



        return self.rating_dao.create_rating(movie_id, rating, user_id)



    def update_rating_with_log(self, rating_id, new_rating):

        return self.rating_dao.update_with_log(rating_id, new_rating)



    def delete_rating(self, rating_id):

        return self.rating_dao.delete(rating_id)



    def get_ratings_by_movie(self, movie_id):

        ratings = self.rating_dao.get_ratings_by_movie(movie_id)

        if not ratings:

            return None, "No ratings found for this movie"

        return [rating.to_dict() for rating in ratings], None



    def get_stat(self, operation):

        if operation not in ['MAX', 'MIN', 'SUM', 'AVG']:

            raise ValueError("Invalid operation. Use 'MAX', 'MIN', 'SUM', or 'AVG'.")



        return self.rating_dao.get_stat(operation)
