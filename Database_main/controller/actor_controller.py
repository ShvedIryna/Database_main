from flask import request, jsonify

from Database_main.service.ActorService import ActorService



actor_service = ActorService()





def get_all_actors():

    actors = actor_service.get_all_actors()

    return jsonify([actor.to_dict() for actor in actors]), 200





def create_actor():

    data = request.json

    new_actor = actor_service.create_actor(data)

    return jsonify(new_actor.to_dict()), 201





def update_actor(actor_id):

    data = request.json

    updated_actor = actor_service.update_actor(actor_id, data)

    if updated_actor:

        return jsonify(updated_actor.to_dict()), 200

    return jsonify({'message': 'Actor not found'}), 404





def delete_actor(actor_id):

    success = actor_service.delete_actor(actor_id)

    if success:

        return jsonify({'message': 'Actor deleted successfully'}), 200

    return jsonify({'message': 'Actor not found'}), 404



def insert_actors():

    try:

        response = actor_service.insert_actors_batch()

        return jsonify(response), 201

    except Exception as e:

        import traceback

        return jsonify({"error": "An unexpected error occurred", "details": traceback.format_exc()}), 500

