from flask import request, jsonify

from Database_main.service.ReviewService import ReviewService



review_service = ReviewService()



def get_all_reviews():

    reviews = review_service.get_all_reviews()

    return jsonify([review.to_dict() for review in reviews]), 200



def get_review_by_id(review_id):

    review = review_service.get_review_by_id(review_id)

    if review:

        return jsonify(review.to_dict()), 200

    return jsonify({'message': 'Review not found'}), 404



def create_review():

    try:

        data = request.json

        new_review = review_service.create_review(data)



        return jsonify({

            "message": "Review created successfully",

            "review": {

                "movie_id": new_review.movie_id,

                "review_text": new_review.review_text,

                "review_date": new_review.review_date,

                "user_name": new_review.user_name

            }

        }), 201

    except Exception as e:

        return jsonify({"error": str(e)}), 400



def update_review(review_id):

    return jsonify({"message": "Update operation is not allowed on the reviews table"}), 403



def delete_review(review_id):

    success = review_service.delete_review(review_id)

    if success:

        return jsonify({'message': 'Review deleted successfully'}), 200

    return jsonify({'message': 'Review not found'}), 404



def get_reviews_by_movie(movie_id):

    data, error = review_service.get_reviews_by_movie(movie_id)

    if error:

        return jsonify({'error': error}), 404

    return jsonify(data), 200

