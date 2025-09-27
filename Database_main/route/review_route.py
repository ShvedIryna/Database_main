from flask import Blueprint
from Database_main.controller.review_controller import (
    get_all_reviews,
    get_review_by_id,
    create_review,
    update_review,
    delete_review,
    get_reviews_by_movie
)

review_bp = Blueprint('review', __name__)

review_bp.route('/reviews', methods=['GET'])(get_all_reviews)
review_bp.route('/reviews/<int:review_id>', methods=['GET'])(get_review_by_id)
review_bp.route('/reviews', methods=['POST'])(create_review)
review_bp.route('/reviews/<int:review_id>', methods=['PUT'])(update_review)
review_bp.route('/reviews/<int:review_id>', methods=['DELETE'])(delete_review)
review_bp.route('/reviews/movies/<int:movie_id>', methods=['GET'])(get_reviews_by_movie)
