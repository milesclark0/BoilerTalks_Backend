from app.models.Database import db, DBreturn, ObjectId
import datetime, re
from app import logger
import hashlib

class CourseManagementMessages:
    MISSING_FIELDS = "Missing required fields for CM"
    NOT_FOUND = "CM not found"
    INVALID_FIELDS = "Invalid fields: "

    CM_EXISTS = "CM for this username already exists"

    CM_CREATED = "CM created successfully"
    CM_UPDATED = "CM updated successfully"
    CM_DELETED = "CM deleted successfully"

    SAVE_ERROR = "CM save error: "
    UPDATE_ERROR = "CM update error: "
    DELETE_ERROR = "CM delete error: "  

    RULES_INVALID = "Rules must be a list of strings"
    BANNED_USERS_INVALID = "Banned users must be a list of dicts"
    WARNED_USERS_INVALID = "Warned users must be a list of dicts"
    APPEALS_INVALID = "Appeals must be a list of dicts"
    REQUESTS_INVALID = "Requests must be a list of strings"
    MODERATORS_INVALID = "Moderators must be a list of strings"
    ANNOUNCEMENTS_INVALID = "Announcements must be a list of strings"
    REPORTS_INVALID = "Reports must be a list of dicts"

    APPEAL_INVALID = "Appeal must be a valid Dict"
    REQUEST_INVALID = "Request must be a valid String"
    WARNED_USER_INVALID = "Warned user must be a valid Dict"
    BANNED_USER_INVALID = "Banned user must be a valid Dict"
    MODERATOR_INVALID = "Moderator must be a valid String"
    RULE_INVALID = "Rule must be a valid String"
    ANNOUNCEMENT_INVALID = "Announcement must be a valid String"
    REPORT_INVALID = "Report must be a valid Dict"

    APPEAL_INVALID_FORMAT_USERNAME = "Appeal does not contain a valid username"
    APPEAL_INVALID_FORMAT_RESPONSE = "Appeal does not contain a valid response"
    APPEAL_INVALID_FORMAT_REASON = "Appeal does not contain a valid reason"
    APPEAL_INVALID_FORMAT_REVIEWED = "Appeal does not contain a valid review"
    APPEAL_INVALID_FORMAT_UNBAN = "Appeal does not contain a valid unban"

    WARNED_USER_INVALID_FORMAT_USERNAME = "Warned user does not contain a valid username"
    WARNED_USER_INVALID_FORMAT_REASON = "Warned user does not contain a valid reason"

    BANNED_USER_INVALID_FORMAT_USERNAME = "Banned user does not contain a valid username"
    BANNED_USER_INVALID_FORMAT_REASON = "Banned user does not contain a valid reason"

    REPORT_INVALID_FORMAT_USERNAME = "Report does not contain a valid username"
    REPORT_INVALID_FORMAT_REASON = "Report does not contain a valid reason"

    CREATION_DATE_INVALID = "Creation date must be a valid datetime object"

class CourseManagement:
    # required fields
    _courseId: ObjectId

    # optional fields
    rules: list[str]
    bannedUsers: list[dict] # { username: str; reason: str }
    prevBannedUsers: list[dict]
    warnedUsers: list[dict] # { username: str; reason: str }
    prevWarnedUsers: list[dict]
    appeals: list[dict] # { username: str; response: str; reason: str; reviewed: bool; unban: bool }
    requests: list[str]
    moderators: list[str]
    announcement: list[str]
    reports: list[dict]  # { username: str; reason: str }

    # non mutable
    _id: ObjectId
    _creationDate: datetime

    # DB collection
    collection = db.CourseManagement


    def __init__(self, courseId: ObjectId, rules = None, bannedUsers = None, prevBannedUsers = None, warnedUsers = None, prevWarnedUsers = None, appeals = None, requests = None, moderators = None, announcements = None, reports = None, creationDate: datetime = None, id: ObjectId = None):
        self._courseId = courseId

        
        # optional fields
        if rules is not None: self._rules = rules
        else: self._rules = []
        if bannedUsers is not None: self._bannedUsers = bannedUsers
        else: self._bannedUsers = []
        if prevBannedUsers is not None: self._prevBannedUsers = prevBannedUsers
        else: self._prevBannedUsers = []
        if warnedUsers is not None: self._warnedUsers = warnedUsers
        else: self._warnedUsers = []
        if prevWarnedUsers is not None: self._prevWarnedUsers = prevWarnedUsers
        else: self._prevWarnedUsers = []
        if appeals is not None: self._appeals = appeals
        else: self._appeals = []
        if requests is not None: self._requests = requests
        else: self._requests = []
        if moderators is not None: self._moderators = moderators
        else: self._moderators = []
        if announcements is not None: self._announcements = announcements
        else: self._announcements = []
        if reports is not None: self._reports = reports
        else: self._reports = []

        if id is not None: self._id = id
        if creationDate is not None: self._creationDate = creationDate 
        else: self._creationDate = datetime.datetime.utcnow()

    def fromDict(data: dict):
        newDict = {}
        if not CourseManagement.hasAllRequiredFields(data):
            logger.warning(CourseManagementMessages.MISSING_FIELDS)
            return None
        for k in ("courseId", "rules", "bannedUsers", "prevBannedUsers", "warnedUsers", "prevWarnedUsers", "appeals", "requests", "moderators", "announcements", "reports", "creationDate", "_id"):
            item = data.get(k, None)
            newDict[k] = item
        return CourseManagement(*newDict.values())
    
    def save(self):
        isValid = self.validateFields()
        if not isValid[0]:
            return DBreturn(False, CourseManagementMessages.SAVE_ERROR + CourseManagementMessages.INVALID_FIELDS, isValid[1])
        try:
            ret = self.collection.find_one({'courseId': self._courseId})
            if ret is not None:
                logger.warning(CourseManagementMessages.CM_EXISTS)
                return DBreturn(False, CourseManagementMessages.CM_EXISTS, None)

            #save CM
            result = self.collection.insert_one(self.formatDict())
            self._id = result.inserted_id
            logger.info(CourseManagementMessages.CM_CREATED)
            return DBreturn(True, CourseManagementMessages.CM_CREATED, self.formatDict())
        except Exception as e:
            return DBreturn(False, CourseManagementMessages.SAVE_ERROR + str(e), None)
    
    def update(self):
        isValid = self.validateFields()
        if not isValid[0]:
            return DBreturn(False, CourseManagementMessages.UPDATE_ERROR + CourseManagementMessages.INVALID_FIELDS, isValid[1])
        try:
            #remove non mutable fields
            id = self.__dict__.pop('_id', None)
            creationDate = self.__dict__.pop('_creationDate', None)
            courseId = self.__dict__.pop('_courseId', None)

            #update profile
            result = self.collection.update_one({"courseId": courseId}, {"$set": self.formatDict()})

            #add id and creation date back to dict
            self.__dict__['_id'] = id
            self.__dict__['_creationDate'] = creationDate
            self.__dict__['_courseId'] = courseId

            #check if profile was updated
            if result.modified_count == 0:
                return DBreturn(False, CourseManagementMessages.UPDATE_ERROR + CourseManagementMessages.NOT_FOUND, self.formatDict())
            return DBreturn(True, CourseManagementMessages.CM_UPDATED, self.formatDict())
        except Exception as e:
            return DBreturn(False, CourseManagementMessages.UPDATE_ERROR + str(e), None) 

    def delete(self):
        try:
            #delete profile
            result = self.collection.delete_one({"courseId": self._courseId})
            if result.deleted_count == 0:
                logger.warning(CourseManagementMessages.NOT_FOUND)
                return DBreturn(False, CourseManagementMessages.DELETE_ERROR + CourseManagementMessages.NOT_FOUND, None)
            #check if profile was deleted
            if result.deleted_count == 0:
                return DBreturn(False, CourseManagementMessages.DELETE_ERROR + CourseManagementMessages.NOT_FOUND, None)
            return DBreturn(True, CourseManagementMessages.CM_DELETED, None)
        except Exception as e:
            logger.error(e)
            return DBreturn(False, CourseManagementMessages.DELETE_ERROR + str(e), None)


    def validateFields(self):
        errors = []
        for validateFunc in [method for method in dir(self) if callable(getattr(self, method)) and method.startswith("validate") and method != "validateFields"]:
            result = getattr(self, validateFunc)()
            if not result[0]:
                errors.extend(result[1])
        return (len(errors) == 0, errors)
    
    def validateRules(self):
        errors = []
        if not isinstance(self._rules, list):
            errors.append(CourseManagementMessages.RULES_INVALID)
        else:
            for rule in self._rules:
                if not isinstance(rule, str):
                    errors.append(CourseManagementMessages.RULE_ENTRY_INVALID)
                    break
        return (len(errors) == 0, errors)
    
    def validateBannedUsers(self):
        errors = []
        if not isinstance(self._bannedUsers, list):
            errors.append(CourseManagementMessages.BANNED_USERS_INVALID)
        else:
            for item in self._bannedUsers:
                if not isinstance(item, dict):
                    errors.append(CourseManagementMessages.BANNED_USER_INVALID)
                if "username" not in item:
                    errors.append(CourseManagementMessages.BANNED_USER_INVALID_FORMAT_USERNAME)
                if "reason" not in item:
                    errors.append(CourseManagementMessages.BANNED_USER_INVALID_FORMAT_REASON)
        return (len(errors) == 0, errors)

    def validateWarnedUsers(self):
        errors = []
        if not isinstance(self._warnedUsers, list):
            errors.append(CourseManagementMessages.WARNED_USERS_INVALID)
        else:
            for item in self._warnedUsers:
                if not isinstance(item, dict):
                    errors.append(CourseManagementMessages.WARNED_USER_INVALID)
                if "username" not in item:
                    errors.append(CourseManagementMessages.WARNED_USER_INVALID_FORMAT_USERNAME)
                if "reason" not in item:
                    errors.append(CourseManagementMessages.WARNED_USER_INVALID_FORMAT_REASON)
        return (len(errors) == 0, errors)
    
    def validateAppeals(self):
        errors = []
        if not isinstance(self._appeals, list):
            errors.append(CourseManagementMessages.APPEALS_INVALID)
        else:
            for appeal in self._appeals:
                if not isinstance(appeal, dict):
                    errors.append(CourseManagementMessages.APPEAL_INVALID)
                if "username" not in appeal:
                    errors.append(CourseManagementMessages.APPEAL_INVALID_FORMAT_USERNAME)
                if "reason" not in appeal:
                    errors.append(CourseManagementMessages.APPEAL_INVALID_FORMAT_REASON)
                if "response" not in appeal:
                    errors.append(CourseManagementMessages.APPEAL_INVALID_FORMAT_RESPONSE)
                if "reviewed" not in appeal:
                    errors.append(CourseManagementMessages.APPEAL_INVALID_FORMAT_REVIEWED)
                if "unban" not in appeal:
                    errors.append(CourseManagementMessages.APPEAL_INVALID_FORMAT_UNBAN)
        return (len(errors) == 0, errors)
    
    def validateRequests(self):
        errors = []
        if not isinstance(self._requests, list):
            errors.append(CourseManagementMessages.REQUESTS_INVALID)
        else:
            for request in self._requests:
                if not isinstance(request, str):
                    errors.append(CourseManagementMessages.REQUEST_INVALID)
                    break
        return (len(errors) == 0, errors)
    
    def validateModerators(self):
        errors = []
        if not isinstance(self._moderators, list):
            errors.append(CourseManagementMessages.MODERATORS_INVALID)
        else:
            for moderator in self._moderators:
                if not isinstance(moderator, str):
                    errors.append(CourseManagementMessages.MODERATOR_INVALID)
                    break
        return (len(errors) == 0, errors)
    
    def validateAnnouncements(self):
        errors = []
        if not isinstance(self._announcements, list):
            errors.append(CourseManagementMessages.ANNOUNCEMENTS_INVALID)
        else:
            for announcement in self._announcements:
                if not isinstance(announcement, str):
                    errors.append(CourseManagementMessages.ANNOUNCEMENT_INVALID)
                    break
        return (len(errors) == 0, errors)
    
    def validateReports(self):
        errors = []
        if not isinstance(self._reports, list):
            errors.append(CourseManagementMessages.REPORTS_INVALID)
        else:
            for item in self._reports:
                if not isinstance(item, dict):
                    errors.append(CourseManagementMessages.REPORT_INVALID)
                if "username" not in item:
                    errors.append(CourseManagementMessages.REPORT_INVALID_FORMAT_USERNAME)
                if "reason" not in item:
                    errors.append(CourseManagementMessages.REPORT_INVALID_FORMAT_REASON)
        return (len(errors) == 0, errors)          
    
    def validateCreationDate(self):
        #try to parse the date if it is a string
        errors = []
        if isinstance(self._creationDate, str):
            try:
                self._creationDate = datetime.datetime.strptime(self._creationDate, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append(CourseManagementMessages.CREATION_DATE_INVALID)
        if not isinstance(self._creationDate, datetime.datetime):
            errors.append(CourseManagementMessages.CREATION_DATE_INVALID)
        return (len(errors) == 0, errors)
    
    # getters and setters
    def getCourseId(self):
        return self._courseId
    
    def getRules(self):
        return self._rules
    
    def getBannedUsers(self):
        return self._bannedUsers

    def getPrevBannedUsers(self):
        return self._prevBannedUsers
    
    def getWarnedUsers(self):
        return self._warnedUsers
    
    def getPrevWarnedUsers(self):
        return self._prevWarnedUsers
    
    def getAppeals(self):
        return self._appeals
    
    def getRequests(self):
        return self._requests
    
    def getModerators(self):
        return self._moderators
    
    def getAnnouncements(self):
        return self._announcements
    
    def getReports(self):
        return self._reports
    
    def getCreationDate(self):
        return self._creationDate
    
    def getId(self):
        return self.__dict__.get("_id", None)


    def setRules(self, rules):
        self._rules = rules

    def setBannedUsers(self, bannedUsers):
        self._bannedUsers = bannedUsers

    def setPrevBannedUsers(self, prevBannedUsers):
        self._prevBannedUsers = prevBannedUsers
    
    def setWarnedUsers(self, warnedUsers):
        self._warnedUsers = warnedUsers

    def setPrevWarnedUsers(self, prevWarnedUsers):
        self._prevWarnedUsers = prevWarnedUsers

    def setAppeals(self, appeals):
        self._appeals = appeals

    def setRequests(self, requests):
        self._requests = requests

    def setAnnouncements(self, announcements):
        self._announcements = announcements

    def setReports(self, reports):
        self._reports = reports

    def setModerators(self, moderators):
        self._moderators = moderators

    def setCreationDate(self, creationDate):
        self._creationDate = creationDate






    @staticmethod
    def hasAllRequiredFields(data: dict):
        if data is None:
            return False
        return all(k in data for k in ["courseId"])
    
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