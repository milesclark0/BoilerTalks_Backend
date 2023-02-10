from app.models.Database import db, DBreturn, ObjectId
import datetime, re
from app import logger

class DmMessages:
    SAVE_ERROR = "Error saving DM: "
    UPDATE_ERROR = "Error updating DM: "
    DELETE_ERROR = "Error deleting DM: "

    NOT_FOUND = "DM not found"
    INVALID_FIELDS = "Invalid fields"

    USER_NULL = "User cannot be null"
    USER_LENGTH = "User must be between 3 and 30 characters"
    USER_NOT_FOUND = "User not found"
    USERS_INVALID = "Users has invalid structure"

    MESSAGE_INVALID = "Message data is invalid"
    MESSAGES_INVALID = "Messages has invalid structure"

    DM_EXISTS = "DM already exists"
    DM_CREATED = "DM created successfully"
    DM_UPDATED = "DM updated successfully"
    DM_DELETED = "DM deleted successfully"

    CREATION_DATE_INVALID = "Creation date is invalid"


class DM:
    _messages: list[dict]

    #non mutable
    _id: ObjectId
    _users: list[2]
    #_roomId: ObjectId
    _creationDate: datetime.datetime

    collection = db.DMs

    def __init__(self, users: list[2], messages: list[dict] = None, id: ObjectId = None, _creationDate: datetime.datetime = None):
        #sort users to make sure they are in the same order when comparing
        #required fields
        self._users = users
        self._users.sort()

        #optional fields
        if messages is not None: self._messages = messages
        else: self._messages = []

        if _creationDate is not None: self._creationDate = _creationDate
        else: self._creationDate = datetime.datetime.now()

        if id is not None: self._id = id

    def fromDict(data: dict):
        newDict = {}
        if DM.hasAllRequiredFields(data) is False:
            logger.warning(DmMessages.INVALID_FIELDS)
            return None
        for k in ("users", "messages", "_id", "_creationDate"):
            item = data.get(k, None)
            newDict[k] = item
        return DM(*newDict.values())


    def save(self):
        #validate Dm
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(DmMessages.INVALID_FIELDS)
            return DBreturn(False, DmMessages.SAVE_ERROR + DmMessages.INVALID_FIELDS, isValid[1])
        try:
            #check if room already exists
            ret = self.collection.find_one({'users': self._users})
            if ret is not None:
                logger.warning(DmMessages.DM_EXISTS)
                return DBreturn(False, DmMessages.DM_EXISTS, ret)

            #check if both users exist
            for user in self._users:
                ret = db.Users.find_one({'username': user})
                if ret is None:
                    logger.warning(DmMessages.USER_NOT_FOUND)
                    return DBreturn(False, DmMessages.USER_NOT_FOUND, None)

            #save room
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(DmMessages.DM_CREATED)
            return DBreturn(True, DmMessages.DM_CREATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, DmMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(DmMessages.INVALID_FIELDS)
            return DBreturn(False, DmMessages.UPDATE_ERROR + DmMessages.INVALID_FIELDS, isValid[1])

        try:
            #remove non mutable fields
            id = self.__dict__.pop("_id", None)
            creationDate = self.__dict__.pop("_creationDate", None)
        

            #update the DM
            result = self.collection.update_one({"users": self._users}, {"$set": self.formatDict()})

            #add non mutable fields back
            self.__dict__["_id"] = id
            self.__dict__["_creationDate"] = creationDate


            if result.modified_count == 0:
                logger.warning(DmMessages.UPDATE_ERROR + DmMessages.NOT_FOUND)
                return DBreturn(False, DmMessages.UPDATE_ERROR + DmMessages.NOT_FOUND, None)
            logger.info(DmMessages.DM_UPDATED)
            return DBreturn(True, DmMessages.DM_UPDATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, DmMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            result = self.collection.delete_one({"users": self._users})
            if result.deleted_count == 0:
                logger.warning(DmMessages.DELETE_ERROR + DmMessages.NOT_FOUND)
                return DBreturn(False, DmMessages.DELETE_ERROR + DmMessages.NOT_FOUND, None)
            logger.info(DmMessages.DM_DELETED)
            return DBreturn(True, DmMessages.DM_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, DmMessages.DELETE_ERROR + str(e), None)

    def validateFields(self):
        # call all validate functions and return a list of errors if any
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate")  and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateUsers(self):
        errors = []
        if not isinstance(self._users, list):
            errors.append(DmMessages.USERS_INVALID)
            return (False, errors)
        if self._users is None:
            logger.warning(DmMessages.USER_NULL)
            errors.append(DmMessages.USER_NULL)
        if self._users is not None:
            for user in self._users:
                if user == "" or user == None:
                    errors.append(DmMessages.USER_NULL)
                    continue
                if len(user) < 3 or len(user) > 30:
                    logger.warning(DmMessages.USER_LENGTH)
                    errors.append(DmMessages.USER_LENGTH)
        return (len(errors) == 0, errors)
    
    def validateMessages(self):
        #messages if they exist must be a list of dicts with the following keys
        #message, username, timestamp
        errors = []
        if not isinstance(self._messages, list):
            errors.append(DmMessages.MESSAGES_INVALID)
            return (False, errors)
        if self._messages is not None:
            for message in self._messages:
                if not isinstance(message, dict):
                    errors.append(DmMessages.MESSAGE_INVALID)
                else:
                    if not all(k in message for k in ("message", "username", "timestamp")):
                        errors.append(DmMessages.MESSAGE_INVALID)
        return (len(errors) == 0, errors)
    
    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(DmMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(DmMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)
    

    
    # getters
    def getId(self):
        #id may not be set yet
        return self.__dict__.get("_id", None)

    def getUsers(self):
        return self._users

    def getCreationDate(self):
        return self._creationDate

    def getMessages(self):
        return self._messages

    # setters
    def setMessages(self, messages):
        self._messages = messages


        # other methods
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

    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all(k in data for k in ["users"])
         


