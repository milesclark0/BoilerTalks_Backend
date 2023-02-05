from app.models.Database import db, DBreturn, ObjectId
import datetime

class Course:
    #None mutable
    _id: ObjectId
    _name: str
    _description: str
    _owner: str
    _department: str
    _memberCount: int = 0
    #None mutable
    _userThread: ObjectId
    #None mutable
    _generalRoom: ObjectId
    #None mutable
    _modRoom: ObjectId
    _semester: str
    _year: int
    #None mutable
    _created: datetime.datetime


    # Database collection
    collection = db.Courses

    def __init__(self, name: str, description: str, owner: str, department: str, semester: str, year: int):
        self._name = name
        self._description = description
        self._owner = owner
        self._department = department
        self._semester = semester
        self._year = year
        self._created = datetime.datetime.utcnow()