from Database_main.database import db
from Database_main.models.country import Country

class CountryDAO:
    def get_all(self):
        return Country.query.all()

    def get_by_code(self, country_code):
        return Country.query.get(country_code)

    def create(self, data):
        new_country = Country(**data)
        db.session.add(new_country)
        db.session.commit()
        return new_country

    def update(self, country_code, data):
        country = Country.query.get(country_code)
        if country:
            for key, value in data.items():
                setattr(country, key, value)
            db.session.commit()
            return country
        return None

    def delete(self, country_code):
        country = Country.query.get(country_code)
        if country:
            db.session.delete(country)
            db.session.commit()
            return True
        return False
