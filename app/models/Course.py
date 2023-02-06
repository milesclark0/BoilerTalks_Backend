from app.models.Database import db, DBreturn, ObjectId
from app.models.Room import Room
from app.models.Thread import Thread
from app import logger
import datetime, re

class CourseMessages:
    MISSING_FIELDS = "Missing required fields for course"
    COURSE_EXISTS = "Course already exists"
    COURSE_NOT_FOUND = "Course not found"
    INVALID_FIELDS = "Invalid fields: "

    COURSE_CREATED = "Course created successfully"
    COURSE_UPDATED = "Course updated successfully"
    COURSE_DELETED = "Course deleted successfully"

    SAVE_ERROR = "Course Save error:"
    UPDATE_ERROR = "Course Update error:"
    DELETE_ERROR = "Course Delete error:"   

    SEMESTER_NULL = "Semester cannot be null or empty"
    INVALID_TERM = "Invalid term"
    INVALID_YEAR = "Invalid year"
    INVALID_SEMESTER = "Invalid semester"

    NAME_NULL = "Name cannot be null or empty"
    NAME_TOO_LONG = "Name cannot be longer than 20 characters"

    INVALID_MEMBER_COUNT = "Member count must be a positive integer"

    DESCRIPTION_NULL = "Description cannot be null or empty"
    DESCRIPTION_TOO_LONG = "Description cannot be longer than 200 characters"

    OWNER_NULL = "Owner cannot be null or empty"
    OWNER_INVALID_LENGTH = "Owner must be between 4 and 20 characters"

    INSTRUCTOR_INVALID_LENGTH = "Instructor must be between 4 and 20 characters"

    DEPARTMENT_NULL = "Department cannot be null or empty"
    DEPARTMENT_INVALID_LENGTH = "Department must be between 4 and 20 characters"

    FOREIGN_KEYS_POPULATED = "Foreign keys successfully populated"
    FOREIGN_KEYS_DELETED = "Foreign keys successfully deleted"
    FOREIGN_KEYS_ERROR = "Error populating foreign keys"

class Course:

    _name: str
    _description: str
    _owner: str
    _instructor: str
    _department: str
    _semester: str
    
    #TODO:auto increment
    _memberCount: int = 0


    #non mutable
    _id: ObjectId
    _userThread: ObjectId
    _generalRoom: ObjectId
    _modRoom: ObjectId
    _creationDate: datetime.datetime


    # Database collection
    collection = db.Courses

    def __init__(self, name: str, description: str, owner: str, department: str, semester: str, instructor: str = None, \
                id: ObjectId = None, memberCount: int = None, userThread: ObjectId = None, \
                generalRoom: ObjectId = None, modRoom: ObjectId = None, creationDate: datetime.datetime = None):
        #required fields
        self._name = name
        self._description = description
        self._owner = owner
        self._department = department
        self._semester = semester

        #optional fields
        if id is not None: self._id = id

        if instructor is not None: self._instructor = instructor
        else: self._instructor = ""

        if memberCount is not None: self._memberCount = memberCount
        else: self._memberCount = 0

        if userThread is not None: self._userThread = userThread
        if generalRoom is not None: self._generalRoom = generalRoom
        if modRoom is not None: self._modRoom = modRoom

        if creationDate is not None: self._creationDate = creationDate
        else : self._creationDate = datetime.datetime.now()

    def fromDict(data: dict):
        newDict = {}
        if not Course.hasAllRequiredFields(data):
            logger.warning(CourseMessages.MISSING_FIELDS)
            return None
        # reorder the dictionary to match the order of the constructor
        for key in ('name', 'description', 'owner', 'department', 'semester', 'instructor', '_id', 'memberCount', 'userThread', 'generalRoom', 'modRoom', 'creationDate'):
            item = data.pop(key, None)
            newDict[key] = item
        return Course(*newDict.values())

    #database methods
    #TODO: delete documents who have no thread or rooms due to error on save
    def save(self):
        #validate course
        isValid = self.validateFields()
        if not isValid[0]:
            return DBreturn(False, CourseMessages.SAVE_ERROR + CourseMessages.INVALID_FIELDS, isValid[1])
        try:
            #check if course already exists
            ret = self.collection.find_one({'name': self._name, 'semester': self._semester})
            if ret is not None:
                logger.warning(CourseMessages.COURSE_EXISTS)
                return DBreturn(False, CourseMessages.COURSE_EXISTS, ret)
            #save course
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(CourseMessages.COURSE_CREATED)

            ret = self.populateForeignKeys()
            #error populating foreign keys
            if not ret.success:
                return ret
            #update course with foreign keys
            ret = self.update()
            if not ret.success:
                return ret
            return DBreturn(True, CourseMessages.COURSE_CREATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, CourseMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            return DBreturn(False, CourseMessages.UPDATE_ERROR + CourseMessages.INVALID_FIELDS, isValid[1])
        try:
            #remove all non mutable fields
            id = self.__dict__.pop('_id', None)
            userThread = self.__dict__.pop('_userThread', None)
            generalRoom = self.__dict__.pop('_generalRoom', None)
            modRoom = self.__dict__.pop('_modRoom', None)
            creationDate = self.__dict__.pop('_creationDate', None)

            #update course
            result = self.collection.update_one({'name': self._name, 'semester': self._semester}, {'$set': self.formatDict()})
            
            #add back non mutable fields
            self._id = id
            self._userThread = userThread
            self._generalRoom = generalRoom
            self._modRoom = modRoom
            self._creationDate = creationDate

            #check if course was updated
            if result.modified_count == 0:
                logger.warning(CourseMessages.COURSE_NOT_FOUND)
                return DBreturn(False, CourseMessages.COURSE_NOT_FOUND, None)
            logger.info(CourseMessages.COURSE_UPDATED)
            return DBreturn(True, CourseMessages.COURSE_UPDATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, CourseMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            #delete all rooms and thread
            ret = self.deleteForeignKeys()
            if not ret.success:
                return ret
            #delete course
            result = self.collection.delete_one({'name': self._name, 'semester': self._semester})
            if result.deleted_count == 0:
                logger.warning(CourseMessages.COURSE_NOT_FOUND)
                return DBreturn(False, CourseMessages.COURSE_NOT_FOUND, None)
            return DBreturn(True, CourseMessages.COURSE_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, CourseMessages.DELETE_ERROR + str(e), None)


    def validateFields(self):
        # call all validate functions and return a list of errors if any
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate")  and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateSemester(self):
        # semester must be in the format "Fall|Spring|Summer|Winter YYYY" and not null
        errors = []
        term, year = None, None
        if self._semester is None or self._semester == "":
            errors.append(CourseMessages.SEMESTER_NULL)
        splitVal = self._semester.split(" ")
        if len(splitVal) != 2:
            errors.append(CourseMessages.INVALID_SEMESTER)
        else:
            term, year = splitVal
        if term not in ("Fall", "Spring", "Summer", "Winter") and term is not None:
            errors.append(CourseMessages.INVALID_TERM)
        if not year.isdigit() and year is not None:
            errors.append(CourseMessages.INVALID_YEAR)
        return (len(errors) == 0, errors)

    def validateMemberCount(self):
        # memberCount must be a positive integer
        errors = []
        if self._memberCount is None or self._memberCount < 0:
            errors.append(CourseMessages.INVALID_MEMBER_COUNT)
        return (len(errors) == 0, errors)

    def validateName(self):
        # name must be between 1 and 20 characters and not null
        errors = []
        if self._name is None or self._name == "":
            errors.append(CourseMessages.NAME_NULL)
        if len(self._name) > 20:
            errors.append(CourseMessages.NAME_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateDescription(self):
        # description must be between 1 and 200 characters and not null
        errors = []
        if self._description is None or self._description == "":
            errors.append(CourseMessages.DESCRIPTION_NULL)
        if len(self._description) > 200:
            errors.append(CourseMessages.DESCRIPTION_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateOwner(self):
        # owner must be between 4 and 20 characters and not null
        errors = []
        if self._owner == "" or self._owner == None:
            errors.append(CourseMessages.OWNER_NULL)
        if len(self._owner) < 4 or len(self._owner) > 20:
            errors.append(CourseMessages.OWNER_INVALID_LENGTH)
        return (len(errors) == 0, errors)

    def validateInstructor(self):
        # instructor must be between 4 and 20 or null
        errors = []
        #only check if instructor is not null or empty
        if self._instructor != "" and self._instructor != None:
            if len(self._instructor) < 4 or len(self._instructor) > 20:
                errors.append(CourseMessages.INSTRUCTOR_INVALID_LENGTH)
        return (len(errors) == 0, errors)

    def validateDepartment(self):
        # department must be between 4 and 20 characters and not null
        errors = []
        if self._department == "" or self._department == None:
            errors.append(CourseMessages.DEPARTMENT_NULL)
        if len(self._department) < 4 or len(self._department) > 20:
            errors.append(CourseMessages.DEPARTMENT_INVALID_LENGTH)
        return (len(errors) == 0, errors)


    #getters
    def getId(self):
        #id may not be set yet
        return self.__dict__.get("_id", None)

    def getName(self):
        return self._name       

    def getDescription(self):
        return self._description    

    def getOwner(self):
        return self._owner  

    def getInstructor(self):
        return self._instructor

    def getDepartment(self):
        return self._department

    def getMemberCount(self):
        return self._memberCount

    def getUserThread(self):
        if self._userThread is not None:
            return self._userThread

    def getGeneralRoom(self):
        if self._generalRoom is not None:
            return self._generalRoom

    def getModRoom(self):
        if self._modRoom is not None:
            return self._modRoom

    def getSemester(self):
        return self._semester

    def getCreationDate(self):
        return self._creationDate

    #setters
    def setName(self, name: str):
        self._name = name

    def setDescription(self, description: str):
        self._description = description

    def setOwner(self, owner: str):
        self._owner = owner

    def setInstructor(self, instructor: str):
        self._instructor = instructor

    def setDepartment(self, department: str):
        self._department = department

    def setMemberCount(self, memberCount: int):
        self._memberCount = memberCount

    def setUserThread(self, userThread: ObjectId):
        self._userThread = userThread

    def setGeneralRoom(self, generalRoom: ObjectId):
        self._generalRoom = generalRoom

    def setModRoom(self, modRoom: ObjectId):
        self._modRoom = modRoom

    def setSemester(self, semester: str):
        self._semester = semester

    def setCreationDate(self, creationDate: datetime.datetime):
        self._creationDate = creationDate

    # other methods
    def populateForeignKeys(self):
        # create a thread and two rooms for the course
        thread = Thread(name=self._name, courseId=self._id)
        threadRet = thread.save()
        if not threadRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)            
            return threadRet
        self._userThread = threadRet.data['_id']

        generalRoom = Room(name=self._name + " General Room", courseId=self._id)
        generalRoomRet = generalRoom.save()
        if not generalRoomRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
            return generalRoomRet
        self._generalRoom = generalRoomRet.data['_id']

        modRoom = Room(name=self._name + " Mod Room", courseId=self._id, isModRoom=True)
        modRoomRet = modRoom.save()
        if not modRoomRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
            return modRoomRet
        self._modRoom = modRoomRet.data['_id']
        return DBreturn(True, CourseMessages.FOREIGN_KEYS_POPULATED, self.formatDict())

    def deleteForeignKeys(self):
        # delete the thread and rooms for the course
        threadRet = Thread.delete(self._userThread)
        if not threadRet.success:
            return threadRet
        generalRoomRet = Room.delete(self._generalRoom)
        if not generalRoomRet.success:
            return generalRoomRet
        modRoomRet = Room.delete(self._modRoom)
        if not modRoomRet.success:
            return modRoomRet
        return DBreturn(True, CourseMessages.FOREIGN_KEYS_DELETED, self.formatDict())


    @staticmethod
    def hasAllRequiredFields(data: dict):
        return all (key in data for key in ("name", "description", "owner", "department", "semester"))

    def __str__(self):
        return str(self.formatDict())

    def formatDict(self):
        # remove the underscore from the beginning of the keys except for _id
        newDict = {}
        for key, value in self.__dict__.items():
            if key == "_id":
                newDict[key] = value
            else:
                newDict[key[1:]] = value
        return newDict





