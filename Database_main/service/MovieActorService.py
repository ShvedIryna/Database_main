from Database_main.dao.MovieActorDAO import MovieActorDAO



class MovieActorService:

    def __init__(self):

        self.movie_actor_dao = MovieActorDAO()



    def get_all_entries(self):

        return self.movie_actor_dao.get_all()



    def get_entry_by_ids(self, movie_id, actor_id):

        return self.movie_actor_dao.get_by_movie_and_actor(movie_id, actor_id)

