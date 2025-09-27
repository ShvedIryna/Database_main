from Database_main.dao.Box_officeDAO import BoxOfficeDAO

class BoxOfficeService:
    def __init__(self):
        self.dao = BoxOfficeDAO()

    def get_all_box_office(self):
        return [entry.to_dict() for entry in self.dao.get_all()]

    def get_box_office_by_id(self, box_office_id):
        entry = self.dao.get_by_id(box_office_id)
        return entry.to_dict() if entry else None

    def create_box_office(self, data):
        return self.dao.create(data).to_dict()

    def update_box_office(self, box_office_id, data):
        entry = self.dao.update(box_office_id, data)
        return entry.to_dict() if entry else None

    def delete_box_office(self, box_office_id):
        return self.dao.delete(box_office_id)
