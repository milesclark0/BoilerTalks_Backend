from app.models.Database import db, DBreturn, ObjectId
import datetime, re
from app import logger

class DmMessages:
    SAVE_ERROR = "Error saving DM"
    UPDATE_ERROR = "Error updating DM"
    DELETE_ERROR = "Error deleting DM"

    NOT_FOUND = "DM not found"
    INVALID_FIELDS = "Invalid fields"

    USER_NULL = "User cannot be null"
    USER_LENGTH = "User must be 24 characters long"
    USER_NOT_FOUND = "User not found"

    DM_EXISTS = "DM already exists"
    DM_CREATED = "DM created successfully"
    DM_UPDATED = "DM updated successfully"
    DM_DELETED = "DM deleted successfully"


class DM:
    _messages: list[dict]

    #non mutable
    _id: ObjectId
    _users: list[2]
    #_roomId: ObjectId
    _creationDate: datetime.datetime

    collection = db.DMs

    def __init__(self, users: list[2], messages: list[dict] = None, id: ObjectId = None, _creationDate: datetime.datetime = datetime.datetime.now()):
        #sort users to make sure they are in the same order when comparing
        #required fields
        self._users = users.sort()

        #optional fields
        if messages is not None: self.messages = messages
        else: self._messages = []

        if _creationDate is not None: self._creationDate = _creationDate
        else: self._creationDate = datetime.datetime.now()

        if id is not None: self._id = id

    def fromDict(self, data: dict):
        newDict = {}
        if DM.hasAllRequiredFields(data) is False:
            logger.warning(DmMessages.INVALID_FIELDS)
            return None
        for k in ("users", "messages", "_id", "_creationDate"):
            item = data.pop(k, None)
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
                ret = db.Users.find_one({'_id': ObjectId(user)})
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
            users = self.__dict__.pop("_users", None)
            creationDate = self.__dict__.pop("_creationDate", None)
        

            #update the DM
            result = self.collection.update_one({"users": self._users}, {"$set": self.formatDict()})

            #add non mutable fields back
            self._id = id
            self._users = users
            self._creationDate = creationDate

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
        for user in self._users:
            if user == "" or user == None:
                errors.append(DmMessages.USER_NULL)
            if len(self._users) < 4 or len(self._users) > 30:
                errors.append(DmMessages.USER_LENGTH)
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
        return all(k in data for k in ("users"))


