from Database_main.database import db



class Movie(db.Model):

    __tablename__ = 'movie'



    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(255), nullable=False)

    release_year = db.Column(db.Integer, nullable=False)

    duration = db.Column(db.Integer, nullable=False)

    description = db.Column(db.Text)

    genre = db.Column(db.String(100))



    def to_dict(self):

        return {

            'movie_id': self.movie_id,

            'title': self.title,

            'release_year': self.release_year,

            'duration': self.duration,

            'description': self.description,

            'genre': self.genre

        }
