from Database_main.dao.Box_officeDAO import BoxOfficeDAO



class BoxOfficeService:

    def __init__(self):

        self.dao = BoxOfficeDAO()



    def get_all_box_office(self):

        return [entry.to_dict() for entry in self.dao.get_all()]



    def get_box_office_by_id(self, box_office_id):

        entry = self.dao.get_by_id(box_office_id)

        return entry.to_dict() if entry else None

