from app.models.Database import db, DBreturn, ObjectId
import datetime, re
from app import logger
import hashlib

class UserMessages:
    SAVE_ERROR = "User Save error: "
    DELETE_ERROR = "User Delete error: "
    UPDATE_ERROR = "User Update error: "
    NOT_FOUND = "User not found"

    FIELDS_INVALID = "Fields invalid"
    MISSING_FIELDS = "Missing required fields for user"

    USERNAME_NULL= "Username cannot be null"
    USERNAME_LENGTH = "Username must be between 3 and 50 characters"
    USERNAME_INVALID = "Username is invalid"

    PASS_NULL = "Password cannot be null"
    PASS_LENGTH = "Password must be between 8 and 100 characters"
    PASS_NUMBER = "Password must contain at least one number"
    PASS_UPPER = "Password must contain at least one uppercase letter"
    PASS_LOWER = "Password must contain at least one lowercase letter"
    PASS_SPECIAL = "Password must contain at least one special character"
    PASS_INVALID = "Password is invalid"

    EMAIL_NULL = "Email cannot be null"
    EMAIL_INVALID = "Email is invalid"

    FIRSTNAME_NULL = "First name cannot be null"
    FIRSTNAME_LENGTH = "First name must be at least 2 characters and less than 50"
    FIRSTNAME_INVALID = "First name is invalid"

    LASTNAME_NULL = "Last name cannot be null"
    LASTNAME_LENGTH = "Last name must be at least 2 characters and less than 50"
    LASTNAME_INVALID = "First name is invalid"


    COURSE_NULL = "A course specified cannot be empty"
    COURSES_INVALID = "A course specified is invalid"

    PROFILE_PICTURE_INVALID = "Profile picture is invalid"
    PROFILE_PICTURE_INVALID_LINK = "Profile picture must be a valid url"

    BLOCKED_USER_NULL = "A user blocked cannot be empty"
    BLOCKED_USERS_INVALID = "A user blocked is invalid"
    
    USERNAME_TAKEN = SAVE_ERROR + "Username already taken"
    EMAIL_TAKEN = SAVE_ERROR + "Email already taken"

    USER_CREATED = "User created successfully"
    USER_DELETED = "User deleted successfully"
    USER_UPDATED = "User updated successfully"

    CREATION_DATE_INVALID = "Creation date must be a valid datetime object"



class User:
    _username: str
    _password: str
    _email: str
    _firstName: str
    _lastName: str
    _courses: list
    _profilePicture: str
    _blockedUsers: list

    #non mutable
    _id: ObjectId
    _creationDate: datetime


    # Database collection
    collection = db.Users


    def __init__(self, username: str, password: str, email: str, firstName: str, lastName: str, courses: list = None, profilePicture: str = None,\
                 blockedUsers: list = None, id: ObjectId = None, creationDate:datetime.datetime = None):
        #required fields
        self._username = username
        self._password = password
        self._email = email
        self._firstName = firstName
        self._lastName = lastName

        #optional fields
        if id is not None: self._id = id
        if courses is not None: self._courses = courses
        else: self._courses = []
        #TODO: add default profile picture link
        if profilePicture is not None: self._profilePicture = profilePicture
        else: self._profilePicture = "https://imgur.com/gallery/mCHMpLT"
        if blockedUsers is not None: self._blockedUsers = blockedUsers
        else: self._blockedUsers = []
        
        if creationDate is not None: self._creationDate = creationDate 
        else: self._creationDate = datetime.datetime.utcnow()

    def fromDict(data: dict):
        newDict = {}
        if not User.hasAllRequiredFields(data):
            logger.warning(UserMessages.MISSING_FIELDS)
            return None
        #reorder dict to match constructor
        for k in ('username', 'password', 'email', 'firstName', 'lastName', 'courses', 'profilePicture', 'blockedUsers', '_id', 'creationDate'):
            item = data.get(k, None)
            newDict[k] = item
        return User(*newDict.values())

    def save(self):
        isValid = self.validateFields(True)
        if not isValid[0]:
            return DBreturn(False, UserMessages.SAVE_ERROR + UserMessages.FIELDS_INVALID, isValid[1])
        #hash password before saving
        self._password = User.hashPassword(self._password)
        try:
            #check if username is taken
            if self.collection.find_one({"username": self._username}) != None:
                return DBreturn(False, UserMessages.USERNAME_TAKEN, self)

            #check if email is taken
            if self.collection.find_one({"email": self._email}) != None:
                return DBreturn(False, UserMessages.EMAIL_TAKEN, self)

            #save user
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            return DBreturn(True, UserMessages.USER_CREATED, self.formatDict())
        except Exception as e:
            return DBreturn(False, UserMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields(False)
        if not isValid[0]:
            return DBreturn(False, UserMessages.UPDATE_ERROR + UserMessages.FIELDS_INVALID, isValid[1])
        try:
            #remove id and creation date from dict to prevent them from being updated
            id = self.__dict__.pop('_id', None)
            creationDate = self.__dict__.pop('_creationDate', None)

            #update user
            result = self.collection.update_one({"username": self._username}, {"$set": self.formatDict()})

            #add id and creation date back to dict
            self.__dict__['_id'] = id
            self.__dict__['_creationDate'] = creationDate

            #check if user was updated
            if result.modified_count == 0:
                return DBreturn(False, UserMessages.UPDATE_ERROR + UserMessages.NOT_FOUND, self)
            return DBreturn(True, UserMessages.USER_UPDATED, self)
        except Exception as e:
            return DBreturn(False, UserMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            #delete user
            result = self.collection.delete_one({"username": self._username})

            #check if user was deleted
            if result.deleted_count == 0:
                return DBreturn(False, UserMessages.DELETE_ERROR + UserMessages.NOT_FOUND, None)
            return DBreturn(True, UserMessages.USER_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, UserMessages.DELETE_ERROR + str(e), None)


    #Validate fields
        
    def validateFields(self, isSave):
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate") and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                #only validate password if saving
                if validateFunc == "validatePassword" and not isSave:
                    continue
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateUsername(self):
        errors = []
        if not isinstance(self._username, str):
            errors.append(UserMessages.USERNAME_INVALID)
            return (False, errors)
        if self._username == "" or self._username == None:
            errors.append(UserMessages.USERNAME_NULL)
        if len(self._username) < 3 or len(self._username) > 50:
            errors.append(UserMessages.USERNAME_LENGTH)
        return (len(errors) == 0, errors)

    def validatePassword(self):
        errors = []
        if not isinstance(self._password, str):
            errors.append(UserMessages.PASS_INVALID)
            return (False, errors)
        if self._password == "" or self._password == None:
            errors.append(UserMessages.PASS_NULL)
        if len(self._password) < 8 or len(self._password) > 100:
            errors.append(UserMessages.PASS_LENGTH)
        if not any(char.isdigit() for char in self._password):
            errors.append(UserMessages.PASS_NUMBER)
        if not any(char.isupper() for char in self._password):
            errors.append(UserMessages.PASS_UPPER)
        if not any(char.islower() for char in self._password):
            errors.append(UserMessages.PASS_LOWER)
        if not any(char in "!@#$%^&*()_+" for char in self._password):
            errors.append(UserMessages.PASS_SPECIAL)
        return (len(errors) == 0, errors)

    def validateEmail(self):
        errors = []
        if not isinstance(self._email, str):
            errors.append(UserMessages.EMAIL_INVALID)
            return (False, errors)
        if self._email == "" or self._email == None:
            errors.append(UserMessages.EMAIL_NULL)
        if re.match(r"(^[a-zA-Z0-9_.+-]+@purdue.edu)$", self._email) == None:
            errors.append(UserMessages.EMAIL_INVALID)
        return (len(errors) == 0, errors)

    def validateFirstName(self):
        errors = []
        if not isinstance(self._firstName, str):
            errors.append(UserMessages.FIRSTNAME_INVALID)
            return (False, errors)
        if self._firstName == "" or self._firstName == None:
            errors.append(UserMessages.FIRSTNAME_NULL)
        if len(self._firstName) > 50 or len(self._firstName) < 2:
            errors.append(UserMessages.FIRSTNAME_LENGTH)
        return (len(errors) == 0, errors)

    def validateLastName(self):
        errors = []
        if not isinstance(self._lastName, str):
            errors.append(UserMessages.LASTNAME_INVALID)
            return (False, errors)
        if self._lastName == "" or self._lastName == None:
            errors.append(UserMessages.LASTNAME_NULL)
        if len(self._lastName) > 50 or len(self._lastName) < 2:
            errors.append(UserMessages.LASTNAME_LENGTH)
        return (len(errors) == 0, errors)

    def validateCourses(self):
        errors = []
        if not isinstance(self._courses, list):
            errors.append(UserMessages.COURSES_INVALID)
            return (False, errors)
        for course in self._courses:
            if course == "" or course == None:
                errors.append(UserMessages.COURSE_NULL)
        return (len(errors) == 0, errors)

    def validateProfilePicture(self):
        errors = []
        if not isinstance(self._profilePicture, str):
            errors.append(UserMessages.PROFILE_PICTURE_INVALID)
            return (False, errors)
        if not (self._profilePicture == "" or self._profilePicture == None):
            if re.match(r"(https:)([/|.|\w|\s|-])*", self._profilePicture) == None:
                errors.append(UserMessages.PROFILE_PICTURE_INVALID_LINK)
        return (len(errors) == 0, errors)

    def validateBlockedUsers(self):
        errors = []
        if not isinstance(self._blockedUsers, list):
            errors.append(UserMessages.BLOCKED_USERS_INVALID)
            return (False, errors)
        for user in self._blockedUsers:
            if user == "" or user == None:
                errors.append(UserMessages.BLOCKED_USER_NULL)
        return (len(errors) == 0, errors)
    
    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(UserMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(UserMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)


    #getters

    def getId(self):
        #id may not be set yet
        return self.__dict__.get("_id", None)

    def getUsername(self):
        return self._username

    def getPassword(self):
        return self._password
    
    def getEmail(self):
        return self._email

    def getFirstName(self):
        return self._firstName

    def getLastName(self):  
        return self._lastName

    def getCourses(self):
        return self._courses

    def getProfilePicture(self):
        return self._profilePicture

    def getBlockedUsers(self):
        return self._blockedUsers

    def getCreationDate(self):
        return self._creationDate
        
    #setters

    def setId(self, id):
        #id may not be set yet
        try:
            return self._id
        except:
            return None

    def setUsername(self, username):
        self._username = username

    def setPassword(self, password):
        self._password = password
    
    def setEmail(self, email):
        self._email = email

    def setFirstName(self, firstName):
        self._firstName = firstName

    def setLastName(self, lastName):
        self._lastName = lastName

    def setCourses(self, courses):
        self._courses = courses

    def setProfilePicture(self, profilePicture):
        self._profilePicture = profilePicture

    def setBlockedUsers(self, blockedUsers):
        self._blockedUsers = blockedUsers

    def setCreationDate(self, creationDate):
        self._creationDate = creationDate


    # Other methods
    @staticmethod
    def hashPassword(password):
        salt = "5gz"
        dataBase_password = password+salt
        hashed = hashlib.md5(dataBase_password.encode())
        return hashed.hexdigest()

    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all(k in data for k in ["username", "password", "email", "firstName", "lastName"])
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

