from flask import request, jsonify
from flasgger import swag_from
from Database_main.service.MovieService import MovieService

movie_service = MovieService()

@swag_from({
    'summary': 'Get a list of all movies',
    'responses': {
        '200': {
            'description': 'Successful request',
            'examples': {
                'application/json': [
                    {'movie_id': 1, 'title': 'The Matrix', 'release_year': 1999, 'duration': 126, 'genre': 'Action', 'description': 'A science fiction action movie'},
                    {'movie_id': 2, 'title': 'Inception', 'release_year': 2010, 'duration': 148, 'genre': 'Sci-Fi', 'description': 'A mind-bending thriller'}
                ]
            }
        }
    }
})

def get_all_movies():
    movies = movie_service.get_all_movies()
    return jsonify([movie.to_dict() for movie in movies]), 200

@swag_from({
    'summary': 'Create a new movie',
    'parameters': [
        {
            'name': 'movie',
            'in': 'body',
            'description': 'New movie data',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'release_year': {'type': 'integer'},
                    'duration': {'type': 'integer'},
                    'description': {'type': 'string'},
                    'genre': {'type': 'string'}
                },
                'required': ['title', 'release_year', 'duration']
            }
        }
    ],
    'responses': {
        '201': {
            'description': 'Movie successfully created',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'movie_id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'release_year': {'type': 'integer'},
                            'duration': {'type': 'integer'},
                            'genre': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})

def create_movie():
    data = request.json
    new_movie = movie_service.create_movie(data)
    return jsonify(new_movie.to_dict()), 201

@swag_from({
    'summary': 'Update movie data',
    'parameters': [
        {
            'name': 'movie_id',
            'in': 'path',
            'description': 'ID of the movie to update',
            'required': True,
            'type': 'integer'
        },
        {
            'name': 'movie',
            'in': 'body',
            'description': 'Data for updating the movie',
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'release_year': {'type': 'integer'},
                    'duration': {'type': 'integer'},
                    'description': {'type': 'string'},
                    'genre': {'type': 'string'}
                }
            }
        }
    ],
    'response': {
        '200': {
            'description': 'Movie successfully update'
        },
        '404': {
            'description': 'Movie not found'
        }
    }
})

def update_movie(movie_id):
    data = request.json
    updated_movie = movie_service.update_movie(movie_id, data)
    if updated_movie:
        return jsonify(updated_movie.to_dict()), 200
    return jsonify({'message': 'Movie not found'}), 404

@swag_from({
    'summary': 'Delete a movie',
    'parameters': [
        {
            'name': 'movie_id',
            'in': 'path',
            'description': 'ID of the movie to delete',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        '200': {
            'description': 'Movie successfully deleted'
        },
        '404': {
            'description': 'Movie not found'
        }
    }
})
def delete_movie(movie_id):
    success = movie_service.delete_movie(movie_id)
    if success:
        return jsonify({'message': 'Movie deleted successfully'}), 200
    return jsonify({'message': 'Movie not found'}), 404
