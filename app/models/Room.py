from app.models.Database import db, DBreturn, ObjectId
from app import logger

class RoomMessages:
    SAVE_ERROR = "Error saving Room: "
    UPDATE_ERROR = "Error updating Room: "
    DELETE_ERROR = "Error deleting Room: "


    INVALID_FIELDS = "Invalid fields"
    MISSING_FIELDS = "Missing fields"
    ROOM_EXISTS = "Room already exists"
    NOT_FOUND = "Room not found"

    CONNECTED_INVALID = "Connected field is not a list"
    CONNECTED_NOT_DICT = "Connected is not a dict"
    CONNECTED_INVALID_FORMAT_SID = "Connected does not contain a valid sid"
    CONNECTED_INVALID_FORMAT_USERNAME = "Connected does not contain a valid username"

    MESSAGES_INVALID = "Messages is not a list"
    MESSAGES_NOT_DICT = "Messages is not a dict"
    MESSAGES_INVALID_FORMAT_USERNAME = "Messages does not contain a valid username"
    MESSAGES_INVALID_FORMAT_MESSAGE = "Messages does not contain a valid message"
    MESSAGES_INVALID_FORMAT_TIME = "Messages does not contain a valid time"

    NAME_TOO_LONG = "Name is too long"
    NAME_NULL = "Name is null"
    NAME_INVALID = "Name is invalid"

    ROOM_CREATED = "Room successfully created"
    ROOM_UPDATED = "Room successfully updated"
    ROOM_DELETED = "Room successfully deleted"

    INVALID_COURSE_ID = "Invalid course id"




class Room:
    _name: str
    _connected: list[dict] #{sid: str, username: str}
    _messages: list[dict] #{username: str, message: str, timeSent: datetime.datetime}
    
    #non mutable
    _id: ObjectId
    _courseId: ObjectId
    #DmId: ObjectId

    collection = db.Rooms

    def __init__(self, name: str, courseId: ObjectId, connected: list[dict] = None, messages: list[dict] = None,  id: ObjectId = None ):
        #required fields
        self._name = name
        self._courseId = courseId

        #optional fields
        if connected is not None: self._connected = connected
        else: self._connected = []

        if messages is not None: self._messages = messages
        else: self._messages = []

        if id is not None: self._id = id

    def fromDict(data: dict):
        newDict = {}
        if not Room.hasAllRequiredFields(data):
            logger.warning(RoomMessages.MISSING_FIELDS)
            return None
        #reorder the dict to match the order of the constructor
        for key in ("name", "courseId", "connected", "messages", "_id"):
            item = data.get(key, None)
            newDict[key] = item
        return Room(*newDict.values())

    def save(self):
        #validate Room
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(RoomMessages.INVALID_FIELDS)
            return DBreturn(False, RoomMessages.SAVE_ERROR + RoomMessages.INVALID_FIELDS, isValid[1])
        try:
            #check if room already exists
            ret = self.collection.find_one({'courseId': self._courseId, 'name': self._name})
            if ret is not None:
                logger.warning(RoomMessages.ROOM_EXISTS)
                return DBreturn(False, RoomMessages.ROOM_EXISTS, ret)
            #save room
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(RoomMessages.ROOM_CREATED)
            return DBreturn(True, RoomMessages.ROOM_CREATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, RoomMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(RoomMessages.INVALID_FIELDS)
            return DBreturn(False, RoomMessages.UPDATE_ERROR + RoomMessages.INVALID_FIELDS, isValid[1])

        try:
            #remove non mutable fields
            id = self.__dict__.pop("_id", None)
            courseId = self.__dict__.pop("_courseId", None)

            #update the ROOM
            result = self.collection.update_one({"_id": ObjectId(id)}, {"$set": self.formatDict()})

            #add non mutable fields back
            self.__dict__["_id"] = id
            self.__dict__["_courseId"] = courseId

            if result.modified_count == 0:
                logger.warning(RoomMessages.UPDATE_ERROR + RoomMessages.NOT_FOUND)
                return DBreturn(True, RoomMessages.UPDATE_ERROR + RoomMessages.NOT_FOUND, None)
            logger.info(RoomMessages.ROOM_UPDATED)
            return DBreturn(True, RoomMessages.ROOM_UPDATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, RoomMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            result = self.collection.delete_one({"courseId": self._courseId})
            if result.deleted_count == 0:
                logger.warning(RoomMessages.DELETE_ERROR + RoomMessages.NOT_FOUND)
                return DBreturn(False, RoomMessages.DELETE_ERROR + RoomMessages.NOT_FOUND, None)
            logger.info(RoomMessages.ROOM_DELETED)
            return DBreturn(True, RoomMessages.ROOM_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, RoomMessages.DELETE_ERROR + str(e), None)
        

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
            errors.append(RoomMessages.NAME_INVALID)
            return (False, errors)
        if self._name is None or self._name == "":
            errors.append(RoomMessages.NAME_NULL)
        if len(self._name) > 100:
            errors.append(RoomMessages.NAME_TOO_LONG)
        return (len(errors) == 0, errors)

    def validateConnected(self):
        # connected must be a list of dict and must have a sid and username
        errors = []
        if not isinstance(self._connected, list):
            errors.append(RoomMessages.CONNECTED_INVALID)
            return (False, errors)
        for item in self._connected:
            if not isinstance(item, dict):
                errors.append(RoomMessages.CONNECTED_NOT_DICT)
            if "sid" not in item:
                errors.append(RoomMessages.CONNECTED_INVALID_FORMAT_SID)
            if "username" not in item:
                errors.append(RoomMessages.CONNECTED_INVALID_FORMAT_USERNAME)
        return (len(errors) == 0, errors)

    def validateMessages(self):
        # messages must be a list of dict and must have a username, message and timeSent
        errors = []
        if not isinstance(self._messages, list):
            errors.append(RoomMessages.MESSAGES_INVALID)
            return (False, errors)
        for item in self._messages:
            if not isinstance(item, dict):
                errors.append(RoomMessages.MESSAGES_NOT_DICT)
            if "username" not in item:
                errors.append(RoomMessages.MESSAGES_INVALID_FORMAT_USERNAME)
            if "message" not in item:
                errors.append(RoomMessages.MESSAGES_INVALID_FORMAT_MESSAGE)
            if "timeSent" not in item:
                errors.append(RoomMessages.MESSAGES_INVALID_FORMAT_TIME)
        return (len(errors) == 0, errors)

    def validateCourseId(self):
        # courseId must be a valid ObjectId
        errors = []
        if not ObjectId.is_valid(self._courseId):
            errors.append(RoomMessages.INVALID_COURSE_ID)
        return (len(errors) == 0, errors)
    


    #getters
    def getId(self):
        return self.__dict__.get("_id", None)

    def getCourseId(self):
        return self._courseId

    def getName(self):
        return self._name

    def getConnected(self): 
        return self._connected

    def getMessages(self):
        return self._messages

    #setters
    def setName(self, name: str):
        self._name = name

    def setConnected(self, connected: list[dict]):  
        self._connected = connected

    def setMessages(self, messages: list[dict]):    
        self._messages = messages

    



    # other methods
    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all (key in data for key in ["name", "courseId"])

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