from flask import request, jsonify
from Database_main.service.BoxOfficeService import BoxOfficeService

box_office_service = BoxOfficeService()

def get_all_box_office():
    entries = box_office_service.get_all_box_office()
    return jsonify(entries), 200

def get_box_office_by_id(box_office_id):
    entry = box_office_service.get_box_office_be_id(box_office_id)
    if entry:
        return jsonify(entry), 200
    return jsonify({'message': 'Box office entry not found'}), 404
