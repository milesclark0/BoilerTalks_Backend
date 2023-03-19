from app.queries import *
from app.queries.courses.aggregates import *

def getAllCourses():
    res = DBreturn()
    try:
        courses = Course.collection.aggregate(get_all_courses_aggregate())
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
        res.data = list(courses)
        #merge courses with same id
        for courseOne in res.data:
            for courseTwo in res.data:
                if courseOne != courseTwo:
                    if courseOne['_id'] == courseTwo['_id']:
                        courseOne['rooms'].extend(courseTwo['rooms'])
                        res.data.remove(courseTwo)
        res.data = parse_json(res.data)
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
        isActiveCourse = courseName in user.getActiveCourses()
        if isActiveCourse:
            user.getActiveCourses().remove(courseName)
        
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


def addRoomToCourse(courseName: str, roomName: str):
    res = DBreturn()
    try:
        course = Course.collection.find_one({"name": courseName})
        if course is None:
            res.message = 'subscribe to course error: Course not found'
            return res

        newRoom = Room(name= courseName+" "+roomName, courseId=course["_id"])
        roomReturn = newRoom.save()
        if not roomReturn.success:
            return roomReturn
        course = Course.fromDict(course)
        course.getRooms().append([newRoom.getName(), newRoom.getId()])
        courseReturn = course.update()
        if not courseReturn.success:
            return courseReturn
        res.success = True
        res.message = 'Successfully added room to course'
        res.data = parse_json(roomReturn.data)
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding room to course ' + courseName
        res.data = str(e)
        print(res.data)
    return res

def getCourseUsers(courseName: str):
    res = DBreturn()
    try:
        users = User.collection.aggregate(get_course_users_aggregate(courseName))
        if users is None:
            res.message = 'get users error: no users found'
            return res
        res.data = parse_json(users)
        res.success = True
        res.message = 'Successfully retrieved user courses'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving users'
        res.data = str(e)
    return res

def getCourseManagementData(courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId": courseId})
        print("Course: " + str(course))
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

def addAppealforCourse(courseId: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId": courseId})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # append to array
        # update coursemanagement
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully added appeal to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding appeal to course'
        res.data = str(e)
    return res

def updateAppealforCourse(courseId: str, descision: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId": courseId})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # if decision is unban, remove user from ban array
        # if decision is deny, update reason in ban array
        # remove the appeal
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully updated ban to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating ban to course'
        res.data = str(e)
    return res

def banUserForCourse(courseId: str, username: str):
    res = DBreturn()
    try:
        course = CourseManagement.collection.find_one({"courseId": courseId})
        if course is None:
            res.message = 'get course error: no course found'
            return res
        # find user from username
        # add user to ban list
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully added user to ban list'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while adding user to ban list'
        res.data = str(e)
    return res