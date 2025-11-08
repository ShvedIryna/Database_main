from flask import Blueprint

from Database_main.controller.genre_controller import (

    get_all_genres,

    get_genre_by_id,

    create_genre,

    update_genre,

    delete_genre

)



genre_bp = Blueprint('genre', __name__)



genre_bp.route('/genres', methods=['GET'])(get_all_genres)

genre_bp.route('/genres/<int:genre_id>', methods=['GET'])(get_genre_by_id)

genre_bp.route('/genres', methods=['POST'])(create_genre)

genre_bp.route('/genres/<int:genre_id>', methods=['PUT'])(update_genre)

genre_bp.route('/genres/<int:genre_id>', methods=['DELETE'])(delete_genre)

