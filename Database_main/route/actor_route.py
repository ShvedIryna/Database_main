from flask import Blueprint

from Database_main.controller.actor_controller import (

    get_all_actors, create_actor, update_actor, delete_actor, insert_actors

)



actor_bp = Blueprint('actor', __name__)



actor_bp.route('/actors', methods=['GET'])(get_all_actors)

actor_bp.route('/actors', methods=['POST'])(create_actor)

actor_bp.route('/actors/<int:actor_id>', methods=['PUT'])(update_actor)

actor_bp.route('/actors/<int:actor_id>', methods=['DELETE'])(delete_actor)

actor_bp.route('/batch-insert', methods=['POST'])(insert_actors)



