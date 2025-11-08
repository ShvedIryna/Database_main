from Database_main.database import db

from Database_main.models.user import User



class UserDAO:

    def get_all(self):

        return User.query.all()



    def get_by_id(self, user_id):

        return User.query.get(user_id)



    def create(self, data):

        new_user = User(**data)

        db.session.add(new_user)

        db.session.commit()

        return new_user



    def update(self, user_id, data):

        user = User.query.get(user_id)

        if user:

            for key, value in data.items():

                setattr(user, key, value)

            db.session.commit()

            return user

        return None



    def delete_user_by_id(self, user_id):

        user = User.query.get(user_id)

        if user:

            db.session.delete(user)

            db.session.commit()

            return True

        return False

