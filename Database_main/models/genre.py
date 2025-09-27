from Database_main.database import db

class Genre(db.Model):
    __tablename__ = 'genre'

    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "genre_id": self.genre_id,
            "genre_name": self.genre_name,
        }

