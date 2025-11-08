import json
import flask.json as flask_json_module

if not hasattr(flask_json_module, 'JSONEncoder'):
    flask_json_module.JSONEncoder = json.JSONEncoder

from Database_main import create_app
from flask import Flask
from flasgger import Swagger
from Database_main.route.actor_route import actor_bp
from Database_main.route.box_office_route import box_office_bp
from Database_main.route.country_route import country_bp
from Database_main.route.genre_route import genre_bp
from Database_main.route.rating_route import rating_bp
from Database_main.route.review_route import review_bp
from Database_main.route.user_route import user_bp
from Database_main.route.movie_route import movie_bp
from Database_main.route.TableRoutes import table_bp

app = create_app()

app.register_blueprint(movie_bp, url_prefix='/api')
app.register_blueprint(actor_bp, url_prefix='/api')
app.register_blueprint(review_bp)
app.register_blueprint(rating_bp)
app.register_blueprint(user_bp)
app.register_blueprint(country_bp)
app.register_blueprint(genre_bp)
app.register_blueprint(box_office_bp)
app.register_blueprint(table_bp)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Movie Database API",
        "description": "REST API for access",
        "version": "1.0.0",
    },
    "basePath": "/api",
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5000)
