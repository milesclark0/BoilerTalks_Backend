from app.models.Database import db, DBreturn, ObjectId
from app.models.Room import Room
from app.models.Thread import Thread
from app.models.CourseManagement import CourseManagement
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

    SAVE_ERROR = "Course Save error: "
    UPDATE_ERROR = "Course Update error: "
    DELETE_ERROR = "Course Delete error: "   

    SEMESTER_NULL = "Semester cannot be null or empty"
    INVALID_TERM = "Invalid term"
    INVALID_YEAR = "Invalid year"
    INVALID_SEMESTER = "Invalid semester"

    NAME_NULL = "Name cannot be null or empty"
    NAME_TOO_LONG = "Name cannot be longer than 20 characters"
    INVALID_NAME = "Invalid name"

    INVALID_MEMBER_COUNT = "Member count must be a positive integer"

    DESCRIPTION_NULL = "Description cannot be null or empty"
    DESCRIPTION_TOO_LONG = "Description cannot be longer than 200 characters"
    INVALID_DESCRIPTION = "Invalid description"

    OWNER_NULL = "Owner cannot be null or empty"
    OWNER_INVALID_LENGTH = "Owner must be between 4 and 20 characters"
    INVALID_OWNER = "Invalid owner"

    INSTRUCTOR_INVALID_LENGTH = "Instructor must be between 4 and 20 characters"
    INVALID_INSTRUCTOR = "Invalid instructor"

    DEPARTMENT_NULL = "Department cannot be null or empty"
    DEPARTMENT_INVALID_LENGTH = "Department must be between 2 and 10 characters"
    INVALID_DEPARTMENT = "Invalid department"

    CREATION_DATE_INVALID = "Creation date must be a valid datetime object"

    FOREIGN_KEYS_POPULATED = "Foreign keys successfully populated"
    FOREIGN_KEYS_DELETED = "Foreign keys successfully deleted"
    FOREIGN_KEYS_ERROR = "Error populating foreign keys"

    QUESTIONS_INVALID = "Questions is not a list"
    QUESTIONS_NOT_DICT = "Questions is not a dict"
    QUESTIONS_INVALID_FORMAT_USERNAME = "Question does not contain a valid username"
    QUESTIONS_INVALID_FORMAT_TITLE = "Question does not contain a title"
    QUESTIONS_INVALID_FORMAT_CONTENT = "Question does not contain content"
    QUESTIONS_INVALID_FORMAT_ANSWERED = "Question does not contain answered flag"

class Course:

    _name: str
    _description: str
    _owner: str
    _instructor: str
    _department: str
    _semester: str
    _questions: list[dict] #{username: str, title: str, content: str, answered: boolean, responses: {answerUsername: str, response: str}[]}
    
    #TODO:auto increment
    _memberCount: int = 0


    #non mutable
    _id: ObjectId
    _userThread: ObjectId
    _rooms: list[list]
    _modRoom: ObjectId
    _creationDate: datetime.datetime


    # Database collection
    collection = db.Courses

    def __init__(self, name: str, description: str, owner: str, department: str, semester: str, instructor: str = None, \
                id: ObjectId = None, memberCount: int = None, userThread: ObjectId = None, \
                rooms: list = [["General Room", None]], modRoom: ObjectId = None, questions: list[dict] = None, creationDate: datetime.datetime = None):
        #required fields
        self._name = name
        self._description = description
        self._owner = owner
        self._department = department
        self._semester = semester

        #optional fields
        # Can be None
        self._instructor = instructor
        self._userThread = userThread
        self._rooms = rooms
        self._modRoom = modRoom
        # Must be initialized
        if id is not None: self._id = id
        if memberCount is not None: self._memberCount = memberCount
        else: self._memberCount = 0
        if creationDate is not None: self._creationDate = creationDate
        else : self._creationDate = datetime.datetime.now()
        if questions is not None: self._questions = questions
        else: self._questions = []

    def fromDict(data: dict):
        newDict = {}
        if not Course.hasAllRequiredFields(data):
            logger.warning(CourseMessages.MISSING_FIELDS)
            return None
        # reorder the dictionary to match the order of the constructor
        for key in ('name', 'description', 'owner', 'department', 'semester', 'instructor', '_id', 'memberCount', 'userThread', 'rooms', 'modRoom', 'questions', 'creationDate'):
            item = data.get(key, None)
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
                return DBreturn(False, CourseMessages.COURSE_EXISTS, None)
            #save course
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(CourseMessages.COURSE_CREATED)

            ret = self.populateForeignKeys()
            #error populating foreign keys
            if not ret.success:
                return ret
            #update course with foreign keys
            ret = self.update(True)
            if not ret.success:
                return ret
            return DBreturn(True, CourseMessages.COURSE_CREATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, CourseMessages.SAVE_ERROR + str(e), None)

    def update(self, isOnInit: bool = False):
        isValid = self.validateFields()
        if not isValid[0]:
            return DBreturn(False, CourseMessages.UPDATE_ERROR + CourseMessages.INVALID_FIELDS, isValid[1])
        try:
            #remove all non mutable fields
            logger.debug(self.__dict__)
            id = self.__dict__.pop('_id', None)
            if not isOnInit:
                userThread = self.__dict__.pop('_userThread', None)
                modRoom = self.__dict__.pop('_modRoom', None)
            creationDate = self.__dict__.pop('_creationDate', None)

            #update course
            logger.warning(self.formatDict())
            result = self.collection.update_one({'name': self._name, 'semester': self._semester}, {'$set': self.formatDict()})
            
            #add back non mutable fields
            self._id = id
            if not isOnInit:
                self.__dict__['_userThread'] = userThread
                self.__dict__['_modRoom'] = modRoom
            self._creationDate = creationDate

            #check if course was updated
            if result.modified_count == 0:
                logger.warning(CourseMessages.COURSE_NOT_FOUND)
                return DBreturn(False, CourseMessages.UPDATE_ERROR + CourseMessages.COURSE_NOT_FOUND, None)
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
                return DBreturn(False, CourseMessages.DELETE_ERROR + CourseMessages.COURSE_NOT_FOUND, None)
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
        if not isinstance(self._semester, str):
            errors.append(CourseMessages.INVALID_SEMESTER)
            return (False, errors)
        term, year = None, None
        if self._semester is None or self._semester == "":
            errors.append(CourseMessages.SEMESTER_NULL)
        splitVal = self._semester.split(" ")
        if len(splitVal) != 2:
            errors.append(CourseMessages.INVALID_SEMESTER)
        else:
            term, year = splitVal
        if term is not None and term not in ("Fall", "Spring", "Summer", "Winter"):
            errors.append(CourseMessages.INVALID_TERM)
        if year is not None and not year.isdigit():
            errors.append(CourseMessages.INVALID_YEAR)
        return (len(errors) == 0, errors)

    def validateMemberCount(self):
        # memberCount must be a positive integer
        errors = []
        if not isinstance(self._memberCount, int):
            errors.append(CourseMessages.INVALID_MEMBER_COUNT)
            return (False, errors)
        
        if self._memberCount is None or self._memberCount < 0:
            errors.append(CourseMessages.INVALID_MEMBER_COUNT)
        return (len(errors) == 0, errors)

    def validateName(self):
        # name must be between 1 and 20 characters and not null
        errors = []
        if not isinstance(self._name, str):
            errors.append(CourseMessages.INVALID_NAME)
            return (False, errors)
        if self._name is None or self._name == "":
            errors.append(CourseMessages.NAME_NULL)
        if len(self._name) > 20:
            errors.append(CourseMessages.NAME_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateDescription(self):
        # description must be between 1 and 200 characters and not null
        errors = []
        if not isinstance(self._description, str):
            errors.append(CourseMessages.INVALID_DESCRIPTION)
            return (False, errors)
        if self._description is None or self._description == "":
            errors.append(CourseMessages.DESCRIPTION_NULL)
        if len(self._description) > 200:
            errors.append(CourseMessages.DESCRIPTION_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateOwner(self):
        # owner must be between 4 and 20 characters and not null
        errors = []
        if not isinstance(self._owner, str):
            errors.append(CourseMessages.INVALID_OWNER)
            return (False, errors)
        if self._owner == "" or self._owner == None:
            errors.append(CourseMessages.OWNER_NULL)
        if len(self._owner) < 4 or len(self._owner) > 50:
            errors.append(CourseMessages.OWNER_INVALID_LENGTH)
        return (len(errors) == 0, errors)

    def validateInstructor(self):
        # instructor must be between 4 and 20 or null
        errors = []
        if not isinstance(self._instructor, str) and self._instructor != None:
            errors.append(CourseMessages.INVALID_INSTRUCTOR)
            return (False, errors)
        #only check if instructor is not null or empty
        if self._instructor != "" and self._instructor != None:
            if len(self._instructor) < 4 or len(self._instructor) > 50:
                errors.append(CourseMessages.INSTRUCTOR_INVALID_LENGTH)
        return (len(errors) == 0, errors)

    def validateDepartment(self):
        # department must be between 4 and 20 characters and not null
        errors = []
        if not isinstance(self._department, str):
            errors.append(CourseMessages.INVALID_DEPARTMENT)
            return (False, errors)
        if self._department == "" or self._department == None:
            errors.append(CourseMessages.DEPARTMENT_NULL)
        if len(self._department) < 2 or len(self._department) > 10:
            errors.append(CourseMessages.DEPARTMENT_INVALID_LENGTH)
        return (len(errors) == 0, errors)
    
    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(CourseMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(CourseMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)
    
    def validateQuestions(self):
        # messages must be a list of dict and must have a username, message and timeSent
        errors = []
        if not isinstance(self._questions, list):
            errors.append(RoomMessages.QUESTIONS_INVALID)
            return (False, errors)
        for item in self._questions:
            if not isinstance(item, dict):
                errors.append(RoomMessages.QUESTIONS_NOT_DICT)
            if "username" not in item:
                errors.append(RoomMessages.QUESTIONS_INVALID_FORMAT_USERNAME)
            if "title" not in item:
                errors.append(RoomMessages.QUESTIONS_INVALID_FORMAT_TITLE)
            if "content" not in item:
                errors.append(RoomMessages.QUESTIONS_INVALID_FORMAT_CONTENT)
            if "answered" not in item:
                errors.append(RoomMessages.QUESTIONS_INVALID_FORMAT_ANSWERED)
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

    def getRooms(self):
        if self._rooms is not None:
            return self._rooms

    def getModRoom(self):
        if self._modRoom is not None:
            return self._modRoom

    def getSemester(self):
        return self._semester

    def getCreationDate(self):
        return self._creationDate
    
    def getQuestions(self):
        return self._questions
    
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

    def setRooms(self, rooms: list[list]):
        self._rooms = rooms

    def setModRoom(self, modRoom: ObjectId):
        self._modRoom = modRoom

    def setSemester(self, semester: str):
        self._semester = semester

    def setCreationDate(self, creationDate: datetime.datetime):
        self._creationDate = creationDate

    def setQuestions(self, questions: list[dict]):
        self._questions = questions

    # other methods
    def populateForeignKeys(self):
        # create a thread and two rooms for the course
        thread = Thread(name=self._name, courseId=self._id)
        threadRet = thread.save()
        if not threadRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)            
            return threadRet
        for i , room in enumerate(self._rooms):
            roomName = room[0]
            generalRoom = Room(name=self._name + " " + roomName, courseId=self._id)
            roomRet = generalRoom.save()
            if not roomRet.success:
                logger.error(roomRet.data)
                logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
                return roomRet
            try:
                self._rooms[i][1] = roomRet.data["_id"]
            except KeyError as e:
                logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
                return DBreturn(False, CourseMessages.FOREIGN_KEYS_ERROR, None)

        modRoom = Room(name=self._name + " Mod Room", courseId=self._id)
        modRoomRet = modRoom.save()
        if not modRoomRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
            return modRoomRet
        
        #create course mngmt object
        courseManagement = CourseManagement(courseId=self._id)
        courseManagementRet = courseManagement.save()
        if not courseManagementRet.success:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
            return courseManagementRet

        try:
            self._userThread = threadRet.data["_id"]
            self._modRoom = modRoomRet.data["_id"]
        except KeyError as e:
            logger.error(CourseMessages.FOREIGN_KEYS_ERROR)
            return DBreturn(False, CourseMessages.FOREIGN_KEYS_ERROR, None)
        return DBreturn(True, CourseMessages.FOREIGN_KEYS_POPULATED, self.formatDict())

    def deleteForeignKeys(self):
        # delete the thread and rooms for the course
        fkError =  DBreturn(False, CourseMessages.FOREIGN_KEYS_ERROR, None)
        userThread = Thread.fromDict(Thread.collection.find_one({"_id": self._userThread}))
        if not isinstance(userThread, Thread):
            return fkError
        threadRet = userThread.delete()
        if not threadRet.success:
            return threadRet
        for i, room in enumerate(self._rooms):
            room = Room.fromDict(Room.collection.find_one({"_id": self._rooms[i][1]}))
            if not isinstance(room, Room):
                return fkError
            roomRet = room.delete()
            if not roomRet.success:
                return roomRet
        modRoom = Room.fromDict(Room.collection.find_one({"_id": self._modRoom}))
        if not isinstance(modRoom, Room):
            return fkError
        modRoomRet = modRoom.delete()
        if not modRoomRet.success:
            return modRoomRet
        courseManagement = CourseManagement.fromDict(CourseManagement.collection.find_one({"courseId": self._id}))
        if not isinstance(courseManagement, CourseManagement):
            return fkError
        courseManagementRet = courseManagement.delete()
        if not courseManagementRet.success:
            return courseManagementRet
        return DBreturn(True, CourseMessages.FOREIGN_KEYS_DELETED, self.formatDict())


    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all (key in data for key in ["name", "description", "owner", "department", "semester"])

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

