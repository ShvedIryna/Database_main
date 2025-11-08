from flask import request, jsonify

from sqlalchemy.exc import OperationalError, SQLAlchemyError

from Database_main.service.RatingService import RatingService



rating_service = RatingService()



def get_all_ratings():

    ratings = rating_service.get_all_ratings()

    return jsonify([rating.to_dict() for rating in ratings]), 200



def get_rating_by_id(rating_id):

    rating = rating_service.get_rating_by_id(rating_id)

    if rating:

        return jsonify(rating.to_dict()), 200

    return jsonify({"message": "Rating not found"}), 404





def update_rating(rating_id):

    data = request.json

    new_rating = data.get("rating")



    if not new_rating or not (1 <= new_rating <= 10):

        return jsonify({"error": "Rating must be between 1 and 10"}), 400



    updated_rating = rating_service.update_rating_with_log(rating_id, new_rating)

    if not updated_rating:

        return jsonify({"error": "Rating not found"}), 404



    return jsonify(updated_rating.to_dict()), 200





def create_rating():

    data = request.get_json()

    if not data or not data.get('movie_id') or not data.get('user_id') or not data.get('rating'):

        return jsonify({"error": "Missing required fields"}), 400



    movie_id = data.get('movie_id')

    user_id = data.get('user_id')

    rating = data.get('rating')



    if not (1 <= rating <= 10):

        return jsonify({"error": "Rating must be between 1 and 10"}), 400



    new_rating = Rating(movie_id=movie_id, user_id=user_id, rating=rating)



    try:

        db.session.add(new_rating)

        db.session.commit()

        return jsonify(new_rating.to_dict()), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({"error": str(e)}), 500



def delete_rating(rating_id):

    try:

        success = rating_service.delete_rating(rating_id)

        if not success:

            return jsonify({"error": "Rating not found"}), 404

        return jsonify({"message": "Rating deleted successfully"}), 200

    except OperationalError as e:

        error_code, error_message = e.orig.args

        if error_code == 1644:

            return jsonify({

                "error": "Database constraint violated.",

                "details": error_message

            }), 403

        return jsonify({

            "error": "Operational error occurred.",

            "details": str(e.orig)

        }), 500

    except SQLAlchemyError as e:

        return jsonify({

            "error": "Database error occurred.",

            "details": str(e)

        }), 500

    except Exception as e:

        return jsonify({

            "error": "Unexpected error occurred.",

            "details": str(e)

        }), 500



def get_rating_stat():

    try:

        operation = request.args.get('operation')

        if not operation:

            return jsonify({"error": "Operation parameter is required."}), 400



        result = rating_service.get_stat(operation)



        return jsonify({

            "operation": operation,

            "result": result

        }), 200

    except ValueError as e:

        return jsonify({"error": str(e)}), 400

    except Exception as e:

        import traceback

        return jsonify({"error": "An unexpected error occurred", "details": traceback.format_exc()}), 500
