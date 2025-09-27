from Database_main.dao.CountryDAO import CountryDAO

class CountryService:
    def __init__(self):
        self.dao = CountryDAO()

    def get_all_countries(self):
        return [country.to_dict() for country in self.dao.get_all()]

    def get_country_by_code(self, country_code):
        country = self.dao.get_by_code(country_code)
        return country.to_dict() if country else None

    def create_country(self, data):
        return self.dao.create(data).to_dict()

    def update_country(self, country_code, data):
        country = self.dao.update(country_code, data)
        return country.to_dict() if country else None

    def delete_country(self, country_code):
        return self.dao.delete(country_code)
