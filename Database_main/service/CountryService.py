from Database_main.dao.CountryDAO import CountryDAO

class CountryService:
    def __init__(self):
        self.dao = CountryDAO()

    def get_all_countries(self):
        return [country.to_dict() for country in self.dao.get_all()]

    def get_country_by_code(self, country_code):
        country = self.dao.get_be_code(country_code)
        return country.to_dict() if country else None
