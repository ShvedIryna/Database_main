from Database_main.database import db
from Database_main.models.movie_actor import Movie_Actor
from Database_main.models.movie import Movie
from Database_main.models.actor import Actor

class MovieActorDAO:
    def get_all(self):
        return Movie_Actor.query.all()

    def get_by_movie_and_actor(self, movie_id, actor_id):
        return Movie_Actor.query.get((movie_id, actor_id))

    def create_movie_actor(self, movie_title, actor_first_name, actor_last_name, role):
        movie = Movie.query.filter_by(title=movie_title).first()
        if not movie:
            raise ValueError(f"Movie with title '{movie_title}' not found.")

        actor = Actor.query.filter_by(first_name=actor_first_name, last_name=actor_last_name).first()
        if not actor:
            raise ValueError(f"Actor '{actor_first_name} {actor_last_name}' not found.")

        existing_entry = Movie_Actor.query.filter_by(movie_id=movie.movie_id, actor_id=actor.actor_id).first()
        if existing_entry:
            raise ValueError(
                f"Relationship between movie '{movie_title}' and actor '{actor_first_name} {actor_last_name}' already exists.")

        new_movie_actor = Movie_Actor(
            movie_id=movie.movie_id,
            actor_id=actor.actor_id,
            role=role
        )
        db.session.add(new_movie_actor)
        db.session.commit()
        return new_movie_actor

    def update(self, movie_id, actor_id, data):
        entry = Movie_Actor.query.get((movie_id, actor_id))
        if entry:
            for key, value in data.items():
                setattr(entry, key, value)
            db.session.commit()
            return entry
        return None

    def delete(self, movie_id, actor_id):
        entry = Movie_Actor.query.get((movie_id, actor_id))
        if entry:
            db.session.delete(entry)
            db.session.commit()


    def get_actors_by_movie(self, movie_id):
        return Movie_Actor.query.filter_by(movie_id=movie_id).all()


    def get_movies_by_actor(self, actor_id):
        return Movie_Actor.query.filter_by(actor_id=actor_id).all()
