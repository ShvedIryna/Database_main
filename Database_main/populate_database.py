import requests
import json
import time
import os

API_URL = os.getenv("API_URL", "https://your-app-name.your-environment-id.polandcentral.azurecontainerapps.io")

def create_movie(title, release_year, duration, description=None, genre=None):
    url = f"{API_URL}/api/movies"
    data = {
        "title": title,
        "release_year": release_year,
        "duration": duration,
        "description": description,
        "genre": genre
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"Created movie: {title}")
        return response.json()
    else:
        print(f"Error creating movie {title}: {response.status_code} - {response.text}")
        return None

def create_actor(first_name, last_name, date_of_birth=None, biography=None):
    url = f"{API_URL}/api/actors"
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": date_of_birth,
        "biography": biography
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"Created actor: {first_name} {last_name}")
        return response.json()
    else:
        print(f"Error creating actor {first_name} {last_name}: {response.status_code} - {response.text}")
        return None

def create_user(username, email, password=None):
    url = f"{API_URL}/api/users"
    data = {
        "username": username,
        "email": email,
        "password": password or "default123"
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"Created user: {username}")
        return response.json()
    else:
        print(f"Error creating user {username}: {response.status_code} - {response.text}")
        return None

def create_rating(movie_id, user_id, rating_value, comment=None):
    url = f"{API_URL}/api/ratings"
    data = {
        "movie_id": movie_id,
        "user_id": user_id,
        "rating": rating_value,
        "comment": comment
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"Created rating: {rating_value}/10 for movie {movie_id}")
        return response.json()
    else:
        print(f"Error creating rating: {response.status_code} - {response.text}")
        return None

def main():
    print("=" * 60)
    print("Populating database with test data")
    print("=" * 60)
    print()

    movies_data = [
        {
            "title": "The Matrix",
            "release_year": 1999,
            "duration": 136,
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "genre": "Sci-Fi"
        },
        {
            "title": "Inception",
            "release_year": 2010,
            "duration": 148,
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "genre": "Sci-Fi"
        },
        {
            "title": "The Dark Knight",
            "release_year": 2008,
            "duration": 152,
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "genre": "Action"
        },
        {
            "title": "Pulp Fiction",
            "release_year": 1994,
            "duration": 154,
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "genre": "Crime"
        },
        {
            "title": "Forrest Gump",
            "release_year": 1994,
            "duration": 142,
            "description": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
            "genre": "Drama"
        }
    ]

    actors_data = [
        {"first_name": "Keanu", "last_name": "Reeves", "date_of_birth": "1964-09-02", "biography": "Canadian actor"},
        {"first_name": "Leonardo", "last_name": "DiCaprio", "date_of_birth": "1974-11-11", "biography": "American actor"},
        {"first_name": "Christian", "last_name": "Bale", "date_of_birth": "1974-01-30", "biography": "British actor"},
        {"first_name": "John", "last_name": "Travolta", "date_of_birth": "1954-02-18", "biography": "American actor"},
        {"first_name": "Tom", "last_name": "Hanks", "date_of_birth": "1956-07-09", "biography": "American actor"}
    ]

    print("Creating movies...")
    created_movies = []
    for movie_data in movies_data:
        movie = create_movie(**movie_data)
        if movie:
            created_movies.append(movie)
        time.sleep(0.5)

    print()
    print("Creating actors...")
    created_actors = []
    for actor_data in actors_data:
        actor = create_actor(**actor_data)
        if actor:
            created_actors.append(actor)
        time.sleep(0.5)

    print()
    print("Creating users...")
    users_data = [
        {"username": "john_doe", "email": "john@example.com"},
        {"username": "jane_smith", "email": "jane@example.com"},
        {"username": "movie_fan", "email": "fan@example.com"}
    ]
    created_users = []
    for user_data in users_data:
        user = create_user(**user_data)
        if user:
            created_users.append(user)
        time.sleep(0.5)

    print()
    print("Creating ratings...")
    if created_movies and created_users:
        ratings_data = [
            {"movie_id": created_movies[0].get("movie_id", 1), "user_id": created_users[0].get("user_id", 1), "rating_value": 9, "comment": "Amazing movie!"},
            {"movie_id": created_movies[1].get("movie_id", 2), "user_id": created_users[0].get("user_id", 1), "rating_value": 10, "comment": "Best sci-fi ever"},
            {"movie_id": created_movies[2].get("movie_id", 3), "user_id": created_users[1].get("user_id", 2), "rating_value": 8, "comment": "Great action movie"},
        ]
        for rating_data in ratings_data:
            create_rating(**rating_data)
            time.sleep(0.5)

    print()
    print("=" * 60)
    print("Database population completed!")
    print("=" * 60)
    print(f"\nCreated:")
    print(f"   - Movies: {len(created_movies)}")
    print(f"   - Actors: {len(created_actors)}")
    print(f"   - Users: {len(created_users)}")
    print(f"\nCheck data:")
    print(f"   - Movies: {API_URL}/api/movies")
    print(f"   - Actors: {API_URL}/api/actors")
    print(f"   - Swagger: {API_URL}/swagger/")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        print(f"API connection error: {e}")
        print(f"Check if API is running at {API_URL}")
    except Exception as e:
        print(f"Error: {e}")
