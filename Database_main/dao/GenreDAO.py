from Database_main.database import db

from Database_main.models.genre import Genre



class GenreDAO:

    def get_all(self):

        return Genre.query.all()



    def get_by_id(self, genre_id):

        return Genre.query.get(genre_id)



    def create(self, data):

        new_genre = Genre(**data)

        db.session.add(new_genre)

        db.session.commit()

        return new_genre



    def update(self, genre_id, data):

        genre = Genre.query.get(genre_id)

        if genre:

            for key, value in data.items():

                setattr(genre, key, value)

            db.session.commit()

            return genre

        return None



    def delete(self, genre_id):

        genre = Genre.query.get(genre_id)

        if genre:

            db.session.delete(genre)

            db.session.commit()

            return True

        return False

