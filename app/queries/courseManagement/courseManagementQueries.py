from app.queries import *

def getCourseManagementData(courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId": ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully retrieved course management'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving course management data'
        res.data = str(e)
    return res

def addCourseMod(username: str, courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.fromDict(CourseManagement.collection.find_one({"courseId": ObjectId(courseId)}))
        if course is None:
            res.message = 'get course error: no course found'
            return res
        profile = Profile.fromDict(Profile.collection.find_one({"username": username}))
        if profile is None:
            res.message = 'bad username'
            return res
        actualCourse = Course.fromDict(Course.collection.find_one({"_id": ObjectId(courseId)}))
        if actualCourse is None:
            res.message = 'bad course'
            return res
        profile.getModThreads().append(actualCourse.getName())
        saveResult = profile.update()
        if not saveResult.success:
            return saveResult
        print(profile.getModThreads())
        course.getModerators().append(username)
        saveResult = course.update()
        if not saveResult.success:
            return saveResult
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while promoting user'
        res.data = str(e)
    return res

def getCourseMods(courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.fromDict(CourseManagement.collection.find_one({"courseId": ObjectId(courseId)}))
        if course is None:
            res.message = 'get course error: no course found'
            return res
        res.data = course.moderators
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while promoting user'
        res.data = str(e)
    return res

def addAppealforCourse(courseId: str, appeal: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # append to array
        course = CourseManagement.fromDict(course)
        course.getAppeals().append(appeal)
        # update coursemanagement
        saveAppeal = course.update()
        if not saveAppeal.success:
            return saveAppeal
        # add notification to any profile who has appeal set on
        courseName = Course.collection.find_one({"_id": ObjectId(courseId)})
        courseName = courseName["name"]
        profiles = Profile.collection.find({})
        for profile in profiles:
            profile = Profile.fromDict(profile)
            for noti in profile.getNotificationPreference():
                if noti["courseName"] == courseName:
                    if noti["appeals"]:
                        profile.getNotification().append({"courseName": courseName, "notification": "appeal", "date": datetime.datetime.utcnow() })
                        saveProfile = profile.update()
                        if not saveProfile.success:
                            return saveProfile
        res.success = True
        res.message = 'Successfully added appeal to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding appeal to course'
        res.data = str(e)
    return res

def updateAppealforCourse(courseId: str, appeal: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        course = CourseManagement.fromDict(course)
        if appeal["unban"]:
            # if decision is unban, remove user from ban array
            banDict = {'username': appeal["username"], 'reason': appeal["reason"]}
            course.getBannedUsers().remove(banDict)
        # update appeal
        appeals = []
        for appealData in course.getAppeals():
            if appealData["id"] == appeal["id"]:
                appealData = appeal
            appeals.append(appealData)
        course.setAppeals(appeals)
        appealRes = course.update()
        if not appealRes.success:
            return appealRes
        res.success = True
        res.message = 'Successfully updated appeal to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating appeal to course'
        res.data = str(e)
    return res

def banUserForCourse(courseId: str, banData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        user = User.collection.find_one({"username": banData["username"]})
        if user is None:
            res.message = 'get user error: no user found'
            return res
        # add user to ban list/prev ban list
        course = CourseManagement.fromDict(course)
        course.getBannedUsers().append(banData)
        course.getPrevBannedUsers().append(banData)
        saveBan = course.update()
        if not saveBan.success:
            return saveBan
        res.success = True
        res.message = 'Successfully added user to ban list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding user to ban list'
        res.data = str(e)
    return res

def warnUserForCourse(courseId: str, warnData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        user = User.collection.find_one({"username": warnData["username"]})
        if user is None:
            res.message = 'get user error: no user found'
            return res
        # add user to warn list/prev warn list 
        course = CourseManagement.fromDict(course)
        course.getWarnedUsers().append(warnData)
        course.getPrevWarnedUsers().append(warnData)
        saveWarning = course.update()
        if not saveWarning.success:
            return saveWarning
        res.success = True
        res.message = 'Successfully added user to warn list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding user to warn list'
        res.data = str(e)
    return res

def updateWarnListForCourse(courseId: str, warnData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        user = User.collection.find_one({"username": warnData["username"]})
        # remove user from warn list
        course = CourseManagement.fromDict(course)
        course.getWarnedUsers().remove(warnData)
        listRes = course.update()
        if not listRes.success:
            return listRes
        res.success = True
        res.message = 'Successfully removed user from warn list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while removing user from warn list'
        res.data = str(e)
    return res

def updateCourseRules(courseId: str, rules: list):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # update rules
        course = CourseManagement.fromDict(course)
        course.setRules(rules)
        rulesRes = course.update()
        if not rulesRes.success:
            return rulesRes
        res.success = True
        res.message = 'Successfully updated course rules'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating course rules'
        res.data = str(e)
    return res

def addReport(courseId: str, reportData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        user = User.collection.find_one({"username": reportData["username"]})
        if user is None:
            res.message = 'get user error: no user found'
            return res
        # add user to report list 
        course = CourseManagement.fromDict(course)
        course.getReports().append(reportData)
        saveReport = course.update()
        if not saveReport.success:
            return saveReport
        res.success = True
        res.message = 'Successfully added report to list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding report to list'
        res.data = str(e)
    return res

def createPoll(courseId: str, pollData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        user = User.collection.find_one({"username": pollData["username"]})
        if user is None:
            res.message = 'get user error: no user found'
            return res
        course = CourseManagement.fromDict(course)
        course.getPolls().append(pollData)
        saveReport = course.update()
        if not saveReport.success:
            return saveReport
        res.success = True
        res.message = 'Successfully added poll to list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding poll to list'
        res.data = str(e)
    return res

def votePoll(courseId: str, voteData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        course = CourseManagement.fromDict(course)
        polls = course.getPolls()
        if polls is None:
            res.message = 'cant vote on empty poll'
            return res
        user = User.collection.find_one({"username": voteData["username"]})
        if user is None:
            res.message = 'get user error: no user found'
            return res
        if voteData["option"] == 1:
            course.getPolls()[voteData["index"]]["one_votes"] += 1
        elif voteData["option"] == 2:
            course.getPolls()[voteData["index"]]["two_votes"] += 1
        elif voteData["option"] == 3:
            course.getPolls()[voteData["index"]]["three_votes"] += 1
        elif voteData["option"] == 4:
            course.getPolls()[voteData["index"]]["four_votes"] += 1
        if course.getPolls()[voteData["index"]]["voted_users"] is None:
            course.getPolls()[voteData["index"]]["voted_users"] = [voteData["username"]]
        else:
            course.getPolls()[voteData["index"]]["voted_users"].append(voteData["username"])
        print(course.getPolls()[voteData["index"]]["voted_users"])
        saveReport = course.update()
        if not saveReport.success:
            return saveReport
        res.success = True
        res.message = 'Successfully added vote to poll'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding vote to poll'
        res.data = str(e)
    return res

def getPolls(courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res 
        course = CourseManagement.fromDict(course)
        res.data = course.getPolls()
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while getting polls'
        res.data = str(e)
    return res

def removeReport(courseId: str, reportData: dict):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId":  ObjectId(courseId)})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        user = User.collection.find_one({"username": reportData["username"]})
        # remove user from warn list
        course = CourseManagement.fromDict(course)
        course.getReports().remove(reportData)
        listRes = course.update()
        if not listRes.success:
            return listRes
        res.success = True
        res.message = 'Successfully removed report from list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while removing report from list'
        res.data = str(e)
    return res

