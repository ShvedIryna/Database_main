from flask import request, jsonify
from Database_main.service.BoxOfficeService import BoxOfficeService

box_office_service = BoxOfficeService()

def get_all_box_office():
    entries = box_office_service.get_all_box_office()
    return jsonify(entries), 200

def get_box_office_by_id(box_office_id):
    entry = box_office_service.get_box_office_by_id(box_office_id)
    if entry:
        return jsonify(entry), 200
    return jsonify({'message': 'Box office entry not found'}), 404

def create_box_office():
    data = request.json
    new_entry = box_office_service.create_box_office(data)
    return jsonify(new_entry), 201

def update_box_office(box_office_id):
    data = request.json
    updated_entry = box_office_service.update_box_office(box_office_id, data)
    if updated_entry:
        return jsonify(updated_entry), 200
    return jsonify({'message': 'Box office entry not found'}), 404

def delete_box_office(box_office_id):
    success = box_office_service.delete_box_office(box_office_id)
    if success:
        return jsonify({'message': 'Box office entry deleted successfully'}), 200
    return jsonify({'message': 'Box office entry not found'}), 404
