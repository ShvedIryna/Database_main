from Database_main.dao.GenreDAO import GenreDAO



class GenreService:

    def __init__(self):

        self.dao = GenreDAO()



    def get_all_genres(self):

        return [genre.to_dict() for genre in self.dao.get_all()]



    def get_genre_by_id(self, genre_id):

        genre = self.dao.get_by_id(genre_id)

        return genre.to_dict() if genre else None



    def create_genre(self, data):

        return self.dao.create(data).to_dict()



    def update_genre(self, genre_id, data):

        genre = self.dao.update(genre_id, data)

        return genre.to_dict() if genre else None



    def delete_genre(self, genre_id):

        return self.dao.delete(genre_id)

