from Database_main.database import db



class BoxOffice(db.Model):

    __tablename__ = 'box_office'



    box_office_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movie_id'), nullable=False)

    country_code = db.Column(db.String(3), db.ForeignKey('country.country_code'), nullable=False)

    box_office_amount = db.Column(db.Numeric(15, 2), nullable=False)

    currency = db.Column(db.String(3), nullable=False)



    def to_dict(self):

        return {

            "box_office_id": self.box_office_id,

            "movie_id": self.movie_id,

            "country_code": self.country_code,

            "box_office_amount": str(self.box_office_amount),

            "currency": self.currency

        }

