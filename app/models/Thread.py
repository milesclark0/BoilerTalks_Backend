from app.models.Database import db, DBreturn, ObjectId
from app import logger

class ThreadMessages:
    SAVE_ERROR = "Error saving Thread: "
    UPDATE_ERROR = "Error updating Thread: "
    DELETE_ERROR = "Error deleting Thread: "

    INVALID_FIELDS = "Invalid fields"
    MISSING_FIELDS = "Missing fields"

    THREAD_SAVED = "Thread saved successfully"
    THREAD_UPDATED = "Thread updated successfully"
    THREAD_DELETED = "Thread deleted successfully"

    NOT_FOUND = "Thread not found"


    NAME_NULL = "Name cannot be null"
    NAME_TOO_LONG = "Name cannot be longer than 20 characters"
    NAME_INVALID = "Name is invalid"

    INVALID_NUMBER_OF_POSTS = "Number of posts must be a positive integer"

    INVALID_COURSE_ID = "Invalid course id"

    THREAD_EXISTS = "Thread already exists"





    

class Thread:
    _name: str

    #TODO:auto increment
    _numberOfPosts: int

    #non mutable
    _id: ObjectId
    _courseId: ObjectId

    collection = db.Threads

    def __init__(self, name: str, courseId: ObjectId, numberOfPosts: int = None,  id: ObjectId = None):
        #required fields
        self._name = name
        self._courseId = courseId

        #optional fields
        if numberOfPosts is not None: self._numberOfPosts = numberOfPosts
        else: self._numberOfPosts = 0
        
        if id is not None: self._id = id

    def fromDict(data: dict):
        newDict = {}
        if Thread.hasAllRequiredFields(data) is False:
            logger.warning(ThreadMessages.MISSING_FIELDS)
            return None
        for k in ("name", "courseId", "numberOfPosts", "_id"):
            item = data.get(k, None)
            newDict[k] = item
        return Thread(*newDict.values())

    def save(self):
        # validate fields
        isValid = self.validateFields()        
        if not isValid[0]:
            logger.warning(ThreadMessages.INVALID_FIELDS)
            return DBreturn(False, ThreadMessages.INVALID_FIELDS, isValid[1])
        try:
            # check if the thread already exists
            ret = self.collection.find_one({"courseId": self._courseId})
            if ret is not None:
                logger.warning(ThreadMessages.THREAD_EXISTS)
                return DBreturn(False, ThreadMessages.THREAD_EXISTS, ret)
            # save the thread
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(ThreadMessages.THREAD_SAVED) 
            return DBreturn(True, ThreadMessages.THREAD_SAVED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, ThreadMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(ThreadMessages.INVALID_FIELDS)
            return DBreturn(False, ThreadMessages.UPDATE_ERROR + ThreadMessages.INVALID_FIELDS, isValid[1])

        try:
            #remove non mutable fields
            id = self.__dict__.pop("_id", None)
            courseId = self.__dict__.pop("_courseId", None)

            #update the thread
            result = self.collection.update_one({"courseId": courseId}, {"$set": self.formatDict()})
            
            #add non mutable fields back
            self.__dict__["_id"] = id
            self.__dict__["_courseId"] = courseId

            if result.modified_count == 0:
                logger.warning(ThreadMessages.UPDATE_ERROR + ThreadMessages.NOT_FOUND)
                return DBreturn(False, ThreadMessages.UPDATE_ERROR + ThreadMessages.NOT_FOUND, None)
            logger.info(ThreadMessages.THREAD_UPDATED)
            return DBreturn(True, ThreadMessages.THREAD_UPDATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, ThreadMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            result = self.collection.delete_one({"courseId": self._courseId})
            if result.deleted_count == 0:
                logger.warning(ThreadMessages.DELETE_ERROR + ThreadMessages.NOT_FOUND)
                return DBreturn(False, ThreadMessages.DELETE_ERROR + ThreadMessages.NOT_FOUND, None)
            logger.info(ThreadMessages.THREAD_DELETED)
            return DBreturn(True, ThreadMessages.THREAD_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, ThreadMessages.DELETE_ERROR + str(e), None)

    def validateFields(self):
        # call all validate functions and return a list of errors if any
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate")  and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateName(self):
        # name must be between 1 and 20 characters and not null
        errors = []
        if not isinstance(self._name, str):
            errors.append(ThreadMessages.NAME_INVALID)
            return (False, errors)
        if self._name is None or self._name == "":
            errors.append(ThreadMessages.NAME_NULL)
        if len(self._name) > 20:
            errors.append(ThreadMessages.NAME_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateCourseId(self):
        # courseId must be a valid ObjectId
        errors = []
        if not ObjectId.is_valid(self._courseId):
            errors.append(ThreadMessages.INVALID_COURSE_ID)
        return (len(errors) == 0, errors)

    def validateNumberOfPosts(self):
        # numberOfPosts must be a positive integer
        errors = []
        if not isinstance(self._numberOfPosts, int):
            errors.append(ThreadMessages.INVALID_NUMBER_OF_POSTS)
            return (False, errors)
        if self._numberOfPosts is None or self._numberOfPosts < 0:
            errors.append(ThreadMessages.INVALID_NUMBER_OF_POSTS)
        return (len(errors) == 0, errors)

    #getters 
    def getName(self):
        return self._name

    def getNumberOfPosts(self):
        return self._numberOfPosts

    def getId(self):    
        #id may not be set yet
        return self.__dict__.get("_id", None)

    def getCourseId(self):
        if self._courseId is not None:
            return self._courseId



    #setters
    def setName(self, name: str):
        self._name = name

    def setNumberOfPosts(self, numberOfPosts: int):
        self._numberOfPosts = numberOfPosts

    def setId(self, id: ObjectId):
        self._id = id

    def setCourseId(self, courseId: ObjectId):
        self._courseId = courseId



    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all(k in data for k in ["name", "courseId"])

    def formatDict(self):
        # remove the underscore from the beginning of the keys except for _id
        newDict = {}
        for key, value in self.__dict__.items():
            if key == "_id":
                newDict[key] = value
            else:
                newDict[key[1:]] = value
        return newDict

    def __str__(self):
        return str(self.formatDict())
    
        
        