from flask import request, jsonify

from Database_main.service.UserService import UserService



user_service = UserService()



def get_all_users():

    users = user_service.get_all_users()

    return jsonify(users), 200



def get_user_by_id(user_id):

    user = user_service.get_user_by_id(user_id)

    if user:

        return jsonify(user), 200

    return jsonify({'message': 'User not found'}), 404



def create_user():

    data = request.json

    new_user = user_service.create_user(data)

    return jsonify(new_user), 201



def update_user(user_id):

    data = request.json

    updated_user = user_service.update_user(user_id, data)

    if updated_user:

        return jsonify(updated_user), 200

    return jsonify({'message': 'User not found'}), 404



def delete_user(user_id):

    try:

        response = user_service.delete_user(user_id)

        return jsonify(response), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 400

