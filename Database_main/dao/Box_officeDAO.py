from Database_main.database import db
from Database_main.models.box_office import BoxOffice

class BoxOfficeDAO:
    def get_all(self):
        return BoxOffice.query.all()

    def get_by_id(self, box_office_id):
        return BoxOffice.query.get(box_office_id)
