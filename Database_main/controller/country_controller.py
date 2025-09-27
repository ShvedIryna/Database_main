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

def create_country():
    data = request.json
    new_country = country_service.create_country(data)
    return jsonify(new_country), 201

def update_country(country_code):
    data = request.json
    updated_country = country_service.update_country(country_code, data)
    if updated_country:
        return jsonify(updated_country), 200
    return jsonify({'message': 'Country not found'}), 404

def delete_country(country_code):
    success = country_service.delete_country(country_code)
    if success:
        return jsonify({'message': 'Country deleted successfully'}), 200
    return jsonify({'message': 'Country not found'}), 404
