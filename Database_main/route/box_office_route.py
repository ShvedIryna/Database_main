from flask import Blueprint

from Database_main.controller.box_office_controller import (get_all_box_office, get_box_office_by_id)



box_office_bp = Blueprint('box_office', __name__)



box_office_bp.route('/box_offices', methods=['GET'])(get_all_box_office)

box_office_bp.route('/box_offices/<int:box_office_id>', methods=['GET'])(get_box_office_by_id)

