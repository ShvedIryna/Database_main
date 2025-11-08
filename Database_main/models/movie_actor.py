from Database_main.database import db



class Movie_Actor(db.Model):

    __tablename__ = 'movie_actor'



    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), primary_key=True)

    actor_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), primary_key=True)

    role = db.Column(db.String(255), nullable=True)



    movie = db.relationship('Movie', backref=db.backref('movie_actors',cascade='all, delete-orphan'))

    actor = db.relationship('Actor', backref=db.backref('movie_actors', cascade='all, delete-orphan'))



    def to_dict(self):

        return {

            'movie_id': self.movie_id,

            'actor_id': self.actor_id,

            'role': self.role,

            'movie': self.movie.title if self.movie else None,

            'actor': f"{self.actor.first_name} {self.actor_last_name}" if self.actor else None

        }

