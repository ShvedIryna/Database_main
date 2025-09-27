from flask import Flask

from Database_main.route.actor_route import actor_bp
from Database_main.route.box_office_route import box_office_bp
from Database_main.route.country_route import country_bp
from Database_main.route.genre_route import genre_bp
from Database_main.route.rating_route import rating_bp
from Database_main.route.review_route import review_bp
from Database_main.route.user_route import user_bp
from Database_main.route.movie_route import movie_bp
from Database_main.route.movie_actor_route import movie_actor_bp
from Database_main.route.movie_genre_route import movie_genre_bp
from Database_main.route.TableRoutes import table_bp
from __init__ import create_app

app = create_app()

app.register_blueprint(movie_bp)
app.register_blueprint(actor_bp)
app.register_blueprint(movie_actor_bp)
app.register_blueprint(review_bp)
app.register_blueprint(rating_bp)
app.register_blueprint(user_bp)
app.register_blueprint(country_bp)
app.register_blueprint(genre_bp)
app.register_blueprint(box_office_bp)
app.register_blueprint(movie_genre_bp)
app.register_blueprint(table_bp)

if __name__ == '__main__':
    app.run(debug=False)

