from Database_main.database import db



class Review(db.Model):

    __tablename__ = 'review'



    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id', ondelete='CASCADE'))

    review_text = db.Column(db.Text)

    review_date = db.Column(db.Date)

    user_name = db.Column(db.String(100))



    movie = db.relationship('Movie', backref=db.backref('reviews', cascade='all, delete-orphan'))



    def to_dict(self):

        return {

            'review_id': self.review_id,

            'movie_id': self.movie_id,

            'review_text': self.review_text,

            'review_date': self.review_date,

            'user_name': self.user_name

        }

