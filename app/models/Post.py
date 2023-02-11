from app.models.Database import db, DBreturn, ObjectId
import datetime, re
from app import logger

class PostMessages:
    SAVE_ERROR = "Error saving Post: "
    UPDATE_ERROR = "Error updating Post: "
    DELETE_ERROR = "Error deleting Post: "

    INVALID_FIELDS = "Invalid fields"

    NOT_FOUND = "Post not found"

    POST_EXISTS = "Post already exists"
    POST_CREATED = "Post created successfully"
    POST_UPDATED = "Post updated successfully"
    POST_DELETED = "Post deleted successfully"

    AUTHOR_NULL = "Author cannot be null"
    TITLE_NULL = "Title cannot be null"
    CONTENT_NULL = "Content cannot be null"
    THREAD_ID_NULL = "ThreadId cannot be null"

    TITLE_LENGTH = "Title must be between 1 and 100 characters"
    TITLE_INVALID = "Title is invalid"

    CONTENT_LENGTH = "Content cannot be longer than 3000 characters"
    CONTENT_INVALID = "Content is invalid"

    AUTHOR_LENGTH = "Author cannot be longer than 50 characters"
    AUTHOR_INVALID = "Author is invalid"

    INVALID_THREAD_ID = "Invalid thread id"

    TOO_MANY_TAGS = "Too many tags"
    TAGS_INVALID = "Invalid tags"


    COMMENT_INVALID = "Invalid comment"
    COMMENTS_INVALID = "Invalid comments structure"

    CREATION_DATE_INVALID = "Invalid creation date"

    ACCEPTED_ANSWER_INVALID = "Invalid accepted answer"

    IS_RESOLVED_INVALID = "Invalid resolved status"









class Post:
    _author: str
    _title: str
    _content: str
    _tags: list[str]
    _comments: list[dict] #{username: str, message: str, timestamp: datetime.datetime}
    _acceptedAnswer: dict
    _isResolved: bool

    #non mutable
    _id: ObjectId
    _threadId: ObjectId
    _creationDate: datetime.datetime

    collection = db.Posts

    def __init__(self, author: str, title: str, content: str, threadId: ObjectId, tags: list[str] = [], \
                comments: list[dict] = None,  acceptedAnswer: dict = None, isResolved: bool = None, id: ObjectId = None, creationDate: datetime.datetime = None):
        #required fields
        self._author = author
        self._title = title
        self._content = content
        self._threadId = threadId

        #optional fields
        if tags is not None: self._tags = tags
        else: self._tags = []

        if comments is not None: self._comments = comments
        else: self._comments = []

        if acceptedAnswer is not None: self._acceptedAnswer = acceptedAnswer
        else : self._acceptedAnswer = {}

        if isResolved is not None: self._isResolved = isResolved
        else: self._isResolved = False


        if creationDate is not None: self._creationDate = creationDate
        else: self._creationDate = datetime.datetime.now()

        if id is not None: self._id = id

    def fromDict(data: dict):
        newDict = {}
        if Post.hasAllRequiredFields(data) is False:
            logger.warning(PostMessages.INVALID_FIELDS)
            return None
        for k in ("author", "title", "content", "threadId", "tags", "comments", "acceptedAnswer", "isResolved", "_id", "_creationDate"):
            item = data.get(k, None)
            newDict[k] = item
        return Post(*newDict.values())

    def save(self):
        #validate Post
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(PostMessages.INVALID_FIELDS)
            return DBreturn(False, PostMessages.SAVE_ERROR + PostMessages.INVALID_FIELDS, isValid[1])
        try:
            #check if POST already exists
            ret = self.collection.find_one({'threadId': self._threadId, 'author': self._author, 'title': self._title})
            if ret is not None:
                logger.warning(PostMessages.POST_EXISTS)
                return DBreturn(False, PostMessages.SAVE_ERROR + PostMessages.POST_EXISTS, ret)
            #save POST
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(PostMessages.POST_CREATED)
            return DBreturn(True, PostMessages.POST_CREATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, PostMessages.SAVE_ERROR + str(e), None)

    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            logger.warning(PostMessages.INVALID_FIELDS)
            return DBreturn(False, PostMessages.UPDATE_ERROR + PostMessages.INVALID_FIELDS, isValid[1])

        try:
            #remove non mutable fields that are not keys
            id = self.__dict__.pop("_id", None)
            creationDate = self.__dict__.pop("_creationDate", None)

            #update the Post
            result = self.collection.update_one({"author": self._author, "title": self._title, "threadId": self._threadId}, {"$set": self.formatDict()})

            #add non mutable fields back
            self.__dict__["_id"] = id
            self.__dict__["_creationDate"] = creationDate

            if result.modified_count == 0:
                logger.warning(PostMessages.UPDATE_ERROR + PostMessages.NOT_FOUND)
                return DBreturn(False, PostMessages.UPDATE_ERROR + PostMessages.NOT_FOUND, None)
            logger.info(PostMessages.POST_UPDATED)
            return DBreturn(True, PostMessages.POST_UPDATED, self.formatDict())
        except Exception as e:
            logger.error(e)
            return DBreturn(False, PostMessages.UPDATE_ERROR + str(e), None)

    def delete(self):
        try:
            result = self.collection.delete_one({"author": self._author, "title": self._title, "threadId": self._threadId})
            if result.deleted_count == 0:
                logger.warning(PostMessages.DELETE_ERROR + PostMessages.NOT_FOUND)
                return DBreturn(False, PostMessages.DELETE_ERROR + PostMessages.NOT_FOUND, None)
            logger.info(PostMessages.POST_DELETED)
            return DBreturn(True, PostMessages.POST_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, PostMessages.DELETE_ERROR + str(e), None)

    def validateFields(self):
        # call all validate functions and return a list of errors if any
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate")  and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)

    def validateAuthor(self):
        errors = []
        if not isinstance(self._author, str):
            errors.append(PostMessages.AUTHOR_INVALID)
            return (False, errors)
        if self._author == "" or self._author == None:
            errors.append(PostMessages.AUTHOR_NULL)
        if len(self._author) < 4 or len(self._author) > 50:
            errors.append(PostMessages.AUTHOR_LENGTH)
        return (len(errors) == 0, errors)
    
    def validateTitle(self):
        errors = []
        if not isinstance(self._title, str):
            errors.append(PostMessages.TITLE_INVALID)
            return (False, errors)
        if self._title == "" or self._title == None:
            errors.append(PostMessages.TITLE_NULL)
        if len(self._title) < 2 or len(self._title) > 100:
            errors.append(PostMessages.TITLE_LENGTH)
        return (len(errors) == 0, errors)

    def validateContent(self):
        errors = []
        if not isinstance(self._content, str):
            errors.append(PostMessages.CONTENT_INVALID)
            return (False, errors)
        if self._content == "" or self._content == None:
            errors.append(PostMessages.CONTENT_NULL)
        if len(self._content) < 4 or len(self._content) > 3000:
            errors.append(PostMessages.CONTENT_LENGTH)
        return (len(errors) == 0, errors)

    def validateTags(self):
        errors = []
        if not isinstance(self._tags, list):
            errors.append(PostMessages.TAGS_INVALID)
            return (False, errors)
        if len(self._tags) > 5:
            errors.append(PostMessages.TOO_MANY_TAGS)
        return (len(errors) == 0, errors)

    def validateComments(self):
        # comments is a list of dicts with keys username, content, timeSent
        errors = []
        if not isinstance(self._comments, list):
            errors.append(PostMessages.COMMENTS_INVALID)
            return (False, errors)
        for comment in self._comments:
            if "username" not in comment or "message" not in comment or "timestamp" not in comment:
                errors.append(PostMessages.COMMENT_INVALID)
        return (len(errors) == 0, errors)

    def validateAcceptedAnswer(self):
        errors = []
        if not isinstance(self._acceptedAnswer, dict):
            errors.append(PostMessages.ACCEPTED_ANSWER_INVALID)
            return (False, errors)
        if self._acceptedAnswer != {}:
            if "username" not in self._acceptedAnswer or "message" not in self._acceptedAnswer or "timestamp" not in self._acceptedAnswer:
                errors.append(PostMessages.ACCEPTED_ANSWER_INVALID)
        return (len(errors) == 0, errors)

    def validateIsResolved(self):
        errors = []
        if isinstance(self._isResolved, bool) is False:
            errors.append(PostMessages.IS_RESOLVED_INVALID)
        return (len(errors) == 0, errors)

    def validateThreadId(self):
        # threadId must be a valid ObjectId
        errors = []
        if not ObjectId.is_valid(self._threadId):
            errors.append(PostMessages.INVALID_THREAD_ID)
        return (len(errors) == 0, errors)
    
    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(PostMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(PostMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)



    #getters
    def getAuthor(self):
        return self._author

    def getTitle(self):
        return self._title

    def getContent(self):
        return self._content

    def getTags(self):
        return self._tags

    def getComments(self):
        return self._comments

    def getAcceptedAnswer(self):
        return self._acceptedAnswer

    def getIsResolved(self):
        return self._isResolved

    def getId(self):
        #id may not be set yet
        return self.__dict__.get("_id", None)

    def getThreadId(self):
        return self._threadId

    def getCreationDate(self):
        return self._creationDate

    #setters
    def setContent(self, content: str):
        self._content = content

    def setTags(self, tags: list[str]):
        self._tags = tags

    def setComments(self, comments: list[dict]):
        self._comments = comments

    def setAcceptedAnswer(self, acceptedAnswer: dict):
        self._acceptedAnswer = acceptedAnswer

    def setIsResolved(self, isResolved: bool):
        self._isResolved = isResolved




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

    @staticmethod
    def hasAllRequiredFields(data: dict):
        return all(k in data for k in ["author", "title", "content", "threadId"])

    def __str__(self):
        return str(self.formatDict())