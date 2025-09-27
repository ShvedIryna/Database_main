from Database_main.database import db
from Database_main.models.box_office import BoxOffice

class BoxOfficeDAO:
    def get_all(self):
        return BoxOffice.query.all()

    def get_by_id(self, box_office_id):
        return BoxOffice.query.get(box_office_id)

    def create(self, data):
        new_entry = BoxOffice(**data)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    def update(self, box_office_id, data):
        entry = BoxOffice.query.get(box_office_id)
        if entry:
            for key, value in data.items():
                setattr(entry, key, value)
            db.session.commit()
            return entry
        return None

    def delete(self, box_office_id):
        entry = BoxOffice.query.get(box_office_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False
