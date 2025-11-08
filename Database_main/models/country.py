from Database_main.database import db



class Country(db.Model):

    __tablename__ = 'country'



    country_code = db.Column(db.String(3), primary_key=True)

    country_name = db.Column(db.String(100), nullable=False)



    def to_dict(self):

        return {

            "country_code": self.country_code,

            "country_name": self.country_name,

        }

