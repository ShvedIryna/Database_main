from Database_main.database import db

from Database_main.models.movie_actor import Movie_Actor

from Database_main.models.movie import Movie

from Database_main.models.actor import Actor



class MovieActorDAO:

    def get_all(self):

        return Movie_Actor.query.all()



    def get_by_movie_and_actor(Self, movie_id, actor_id):

        return Movie_Actor.query.get((movie_id, actor_id))

