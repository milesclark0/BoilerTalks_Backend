from app.queries import *
from app.queries.courses.aggregates import *

def getAllCourses():
    res = DBreturn()
    try:
        courses = Course.collection.find({})
        res.data = parse_json(courses)
        res.success = True
        res.message = 'Successfully retrieved all courses'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving all courses'
        res.data = str(e)
    return res

def setCourseActive(courseName: str, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'set Course Active error: User not found'
            return res
        course = Course.collection.find_one({"name": courseName})
        if course is None:
            res.message = 'set Course Active error: Course not found'
            return res
        user = User.fromDict(user)
        isAlreadyActive = courseName in user.getActiveCourses()
        if isAlreadyActive:
            user.getActiveCourses().remove(courseName)
            userSaveResult = user.update()
            res.data = 'removing'
            if not userSaveResult.success:
                return userSaveResult
        else:
            user.getActiveCourses().append(courseName)
            userSaveResult = user.update()
            res.data = 'adding'
            if not userSaveResult.success:
                return userSaveResult
        res.success = True
        res.message = 'Successfully switched courses active state'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while setting course to active'
        res.data = str(e)
    return res

def getCourse(name: str):
    res = DBreturn()
    try:
        course = Course.collection.find({"name": name})
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully retrieved course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving course'
        res.data = str(e)
    return res
 
def getUserCourses(username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'get user courses error: User not found'
            return res
        aggregate = get_course_aggregate(user)
        courses = Course.collection.aggregate(aggregate)
        res.data = parse_json(courses)
        res.success = True
        res.message = 'Successfully retrieved user courses'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving user courses'
        res.data = str(e)
    return res


def subscribeToCourse(courseName: str, username: str):
    res = DBreturn()
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            res.message = 'subscribe to course error: User not found'
            return res
        courses = Course.collection.find({"name": courseName})
        if courses is None:
            res.message = 'subscribe to course error: Course not found'
            return res
        isAlreadySubscribed = courseName in user.getCourses()
        if isAlreadySubscribed:
            res.message = 'subscribe to course error: Already subscribed to course'
            return res
        user.getCourses().append(courseName)
        userSaveResult = user.update()
        if not userSaveResult.success:
            print(userSaveResult.message)
            return userSaveResult
        # subscribe to every course (all semesters)
        for courseDict in courses:
            course = Course.fromDict(courseDict)
            if course is None:
                res.message = "Unable to subscribe to course: " + courseName
                return res
            course.setMemberCount(course.getMemberCount() + 1)
            courseSaveResult = course.update()
            if not courseSaveResult.success:
                return courseSaveResult
        res.success = True
        res.message = 'Successfully subscribed to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while subscribing to course ' + courseName
        res.data = str(e)
        print(res.data)
    return res

def unsubscribeFromCourse(courseName: str, username: str):
    res = DBreturn()
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            res.message = 'unsubscribe from course error: User not found'
            return res
        courses = Course.collection.find({"name": courseName})
        if courses is None:
            res.message = 'unsubscribe from course error: Course not found'
            return res
        isNotSubscribed = courseName not in user.getCourses()
        if isNotSubscribed:
            res.message = 'unsubscribe from course error: Not subscribed to course'
            return res
        user.getCourses().remove(courseName)
        userSaveResult = user.update()
        if not userSaveResult.success:
            return userSaveResult
        # unsubscribe from every course (all semesters)
        for courseDict in courses:
            course = Course.fromDict(courseDict)
            if course is None:
                res.message = "Unable to unsubscribe from course: " + courseName
                return res
            course.setMemberCount(course.getMemberCount() - 1 if course.getMemberCount() > 0 else 0)
            courseSaveResult = course.update()
            if not courseSaveResult.success:
                return courseSaveResult
        res.success = True
        res.message = 'Successfully unsubscribed from course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while unsubscribing from course ' + courseName
        res.data = str(e)
        print(res.data)
    return res



        
        


