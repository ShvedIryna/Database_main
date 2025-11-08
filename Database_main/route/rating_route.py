from flask import Blueprint

from Database_main.controller.rating_controller import (

    get_all_ratings,

    get_rating_by_id,

    create_rating,

    update_rating,

    delete_rating,

    get_rating_stat

)



rating_bp = Blueprint("rating", __name__)



rating_bp.route("/ratings", methods=["GET"])(get_all_ratings)

rating_bp.route("/ratings/<int:rating_id>", methods=["GET"])(get_rating_by_id)

rating_bp.route("/ratings", methods=["POST"])(create_rating)

rating_bp.route("/ratings/<int:rating_id>", methods=["PUT"])(update_rating)

rating_bp.route("/ratings/<int:rating_id>", methods=["DELETE"])(delete_rating)

rating_bp.route("/ratings/stat", methods=["GET"])(get_rating_stat)

