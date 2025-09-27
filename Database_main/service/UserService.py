from flask import abort
from Database_main.dao.UserDAO import UserDAO
from Database_main.dao.RatingDAO import RatingDAO

class UserService:
    def __init__(self):
        self.user_dao = UserDAO()
        self.rating_dao = RatingDAO()

    def get_all_users(self):
        return [user.to_dict() for user in self.user_dao.get_all()]

    def get_user_by_id(self, user_id):
        user = self.user_dao.get_by_id(user_id)
        return user.to_dict() if user else None

    def create_user(self, data):
        return self.user_dao.create(data).to_dict()

    def update_user(self, user_id, data):
        user = self.user_dao.update(user_id, data)
        return user.to_dict() if user else None

    def delete_user(self, user_id):
        related_rating = self.rating_dao.get_ratings_by_user(user_id)
        if related_rating:
            abort(400, description="Cannot delete user: user_id has associated ratings.")

        is_deleted = self.user_dao.delete_user_by_id(user_id)
        if not is_deleted:
            abort(404, description="User not found.")
        return {"message": f"User with ID {user_id} deleted successfully."}
