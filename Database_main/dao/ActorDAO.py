from Database_main.database import db

from Database_main.models.actor import Actor





class ActorDAO:

    def get_all(self):

        return Actor.query.all()





    def create(self, data):

        new_actor = Actor(**data)

        db.session.add(new_actor)

        db.session.commit()

        return new_actor





    def update(self, actor_id, data):

        actor = Actor.query.get(actor_id)

        if actor:

            for key, value in data.items():

                setattr(actor, key, value)

            db.session.commit()

            return actor

        return None





    def delete(self, actor_id):

        actor = Actor.query.get(actor_id)

        if actor:

            db.session.delete(actor)

            db.session.commit()

            return True

        return False



    def insert_actors_batch(self):

        for i in range(1, 11):

            new_actor = Actor(

                first_name=f"Noname{i}",

                last_name=f"Lastname{i}",

                date_of_birth=None,

                biography=None

            )

            db.session.add(new_actor)

        db.session.commit()

        return {"message": "10 actors added successfully."}

