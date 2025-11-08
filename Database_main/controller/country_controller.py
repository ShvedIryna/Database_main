from flask import request, jsonify

from Database_main.service.CountryService import CountryService



country_service = CountryService()



def get_all_countries():

    countries = country_service.get_all_countries()

    return jsonify(countries), 200



def get_country_by_code(country_code):

    country = country_service.get_country_by_code(country_code)

    if country:

        return jsonify(country), 200

    return jsonify({'message': 'Country not found'}), 404

