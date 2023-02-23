from app.models.Database import db, DBreturn, ObjectId
from app.models.User import User
import datetime, re
from app import logger
import hashlib

class ProfileMessages:
    MISSING_FIELDS = "Missing required fields for profile"
    NOT_FOUND = "Profile not found"
    INVALID_FIELDS = "Invalid fields: "

    PROFILE_EXISTS = "A profile already exists for this user"

    PROFILE_CREATED = "Profile created successfuly"
    PROFILE_UPDATED = "Profile updated successfully"
    PROFILE_DELETED = "Profile deleted successfully"

    SAVE_ERROR = "Profile save error: "
    UPDATE_ERROR = "Profile update error: "
    DELETE_ERROR = "Profile delete error: "  

    INVALID_BIO = "Invalid bio"
    BIO_LENGTH = "Bio must be 500 characters or less"

    INVALID_USER = "Invalid user"
    USER_NULL = "User cannot be null or empty"
    
    MOD_THREAD_NULL = "A modded thread specified cannot be empty"
    MOD_THREADS_INVALID = "Modded thread list is invalid"
    MOD_THREAD_STRING = "A modded thread specified must be a string"

    CREATION_DATE_INVALID = "Creation date must be a valid datetime object"

class Profile:
    _user: User
    _bio: str
    _modThreads: list

    # non mutable
    _id: ObjectId
    _creationDate: datetime

    # DB collection
    collection = db.Profiles

    def __init__(self, user: User, bio: str, modThreads: list, id: ObjectId = None, creationDate: datetime.datetime = None):
        # required fields
        self._user = user
        
        # optional fields
        if id is not None: self._id = id
        if bio is not None: self._bio = bio
        else: self._bio = ""
        if modThreads is not None: self._modThreads = modThreads
        else: self._modThreads = []
        if creationDate is not None: self._creationDate = creationDate 
        else: self._creationDate = datetime.datetime.utcnow()

    def fromDict(data: dict):
        newDict = {}
        if not Profile.hasAllRequiredFields(data):
            logger.warning(ProfileMessages.MISSING_FIELDS)
            return None
        for k in ('user', 'bio', 'modCourses', '_id', 'creationDate'):
            item = data.get(k, None)
            newDict[k] = item
        return Profile(*newDict.values())

    # TODO: make sure this happens upon account creation
    def save(self):
        isValid = self.validateFields(True)
        if not isValid[0]:
            return DBreturn(False, ProfileMessages.SAVE_ERROR + ProfileMessages.FIELDS_INVALID, isValid[1])
        try:
            #check if profile under this username already exists
            ret = self.collection.find_one({'user': self._user})
            if ret is not None:
                logger.warning(ProfileMessages.PROFILE_EXISTS)
                return DBreturn(False, ProfileMessages.PROFILE_EXISTS, None)
            #save profile
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(ProfileMessages.PROFILE_CREATED)

            return DBreturn(True, ProfileMessages.PROFILE_CREATED, self.formatDict())
        except Exception as e:
            return DBreturn(False, ProfileMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields(False)
        if not isValid[0]:
            return DBreturn(False, ProfileMessages.UPDATE_ERROR + ProfileMessages.INVALID_FIELDS, isValid[1])
        try:
            #remove id and creation date from dict to prevent them from being updated
            id = self.__dict__.pop('_id', None)
            creationDate = self.__dict__.pop('_creationDate', None)

            #update user
            result = self.collection.update_one({"user": self._user}, {"$set": self.formatDict()})

            #add id and creation date back to dict
            self.__dict__['_id'] = id
            self.__dict__['_creationDate'] = creationDate

            #check if profile was updated
            if result.modified_count == 0:
                return DBreturn(False, ProfileMessages.UPDATE_ERROR + ProfileMessages.NOT_FOUND, self)
            return DBreturn(True, ProfileMessages.PROFILE_UPDATED, self)
        except Exception as e:
            return DBreturn(False, ProfileMessages.UPDATE_ERROR + str(e), None)   

    def delete(self):
        try:
            #delete profile
            result = self.collection.delete_one({"user": self._user})

            #check if profile was deleted
            if result.deleted_count == 0:
                return DBreturn(False, ProfileMessages.DELETE_ERROR + ProfileMessages.NOT_FOUND, None)
            return DBreturn(True, ProfileMessages.PROFILE_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, ProfileMessages.DELETE_ERROR + str(e), None)


    # field validation

    def validateFields(self):
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate") and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateUser(self):
        errors = []
        if not isinstance(self._user, User) or len(self._user.validateFields(False)) != 0:
            errors.append(ProfileMessages.INVALID_USER)
            return (False, errors)
        return (len(errors) == 0, errors)

    def validateBio(self):
        errors = []
        if not isinstance(self._bio, str):
            errors.append(ProfileMessages.INVALID_BIO)
            return (False, errors)
        if len(self._bio) > 500:
            errors.append(ProfileMessages.BIO_LENGTH)
        return (len(errors) == 0, errors)

    def validateModThreads(self):
        errors = []
        if not isinstance(self._modThreads, list):
            errors.append(ProfileMessages.MOD_THREADS_INVALID)
            return (False, errors)
        for modThread in self._modThreads:
            if not isinstance(modThread, str):
                errors.append(ProfileMessages.MOD_THREAD_STRING)
                return (False, errors)
            if modThread == "" or modThread == None:
                errors.append(ProfileMessages.MOD_THREAD_NULL)
        return (len(errors) == 0, errors)

    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(ProfileMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(ProfileMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)

    # getters and setters

    def getId(self):
        #id may not be set yet
        return self.__dict__.get("_id", None)
    
    def getUser(self):
        return self._user

    def getBio(self):
        return self._bio
    
    def getModThreads(self):
        return self._modThreads
    
    def getCreationDate(self):
        return self._creationDate

    def setId(self, id):
        #id may not be set yet
        try:
            return self._id
        except:
            return None   
    
    def setUser(self, user):
        self._user = user
    
    def setBio(self, bio):
        self._bio = bio

    def setModThreads(self, modThreads):
        self._modThreads = modThreads

    def setCreationDate(self, creationDate):
        self._creationDate = creationDate

    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all(k in data for k in ["user"])
    
    def formatDict(self):
        # remove the underscore from the keys except for _id field
        newDict = {}
        for key, value in self.__dict__.items():
            if key == "_id":
                newDict[key] = value
            else:
                newDict[key[1:]] = value
        return newDict

    def __str__(self):
        return str(self.formatDict())
