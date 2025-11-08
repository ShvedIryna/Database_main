from flask import Blueprint

from Database_main.controller.country_controller import (get_all_countries, get_country_by_code)



country_bp = Blueprint('country', __name__)



country_bp.route('/countries', methods=['GET'])(get_all_countries)

country_bp.route('/countries/<string:country_code>', methods=['GET'])(get_country_by_code)

