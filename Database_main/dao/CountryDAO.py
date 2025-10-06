from Database_main.database import db
from Database_main.models.country import Country

class CountryDAO:
    def get_all(self):
        return Country.query.all()

    def get_by_code(Self, country_code):
        return Country.query.get(country_code)
