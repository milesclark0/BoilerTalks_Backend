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

def getRoom(roomId: str):
    res = DBreturn()
    try:
        room = Room.collection.find_one({"_id": ObjectId(roomId)})
        if room is None:
            res.message = 'get room error: Room not found'
            return res
        res.data = parse_json(room)
        res.success = True
        res.message = 'Successfully retrieved room'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving room'
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
        print(e)
        res.message = 'Error occurred while retrieving user courses'
        res.data = str(e)
    return res

def getUserCoursesAndRooms(username: str):
    courses = getUserCourses(username)
    if not courses.success:
        return courses
    courses = courses.data
    rooms = []
    for course in courses:
        rooms.extend(course['rooms'])
        for i, room in enumerate(course['rooms']):
            #condense room data
            course['rooms'][i] = [room['name'], room['_id']]
    return  DBreturn(True, "SuccessFully got user courses and Rooms", [courses, rooms])



def subscribeToCourse(courseName: str, username: str):
    res = DBreturn()
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        profile = Profile.fromDict(Profile.collection.find_one({"username": username}))
        if user is None:
            res.message = 'subscribe to course error: User not found'
            return res
        if profile is None:
            res.message = 'subscribe to course error: Profile not found'
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
        notificationPreferenceDict = {"messages": True, "appeals": False, "reports": False}
        profile.getNotificationPreference()[courseName] = notificationPreferenceDict
        profileSaveResult = profile.update()
        if not userSaveResult.success:
            print(userSaveResult.message)
            return userSaveResult
        if not profileSaveResult.success:
            print(profileSaveResult.message)
            return profileSaveResult
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
        res = getUserCoursesAndRooms(username)
        if not res.success:
            return res
        res.data = res.data[0] #return only courses
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
        profile = Profile.fromDict(Profile.collection.find_one({"username": username}))
        if user is None:
            res.message = 'unsubscribe from course error: User not found'
            return res
        if profile is None:
            res.message = 'unsubscribe from course error: Profile not found'
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
        for index in range(len(profile.getNotificationPreference())):
            if profile.getNotificationPreference()[index]['courseName'] == courseName:
                del profile.getNotificationPreference()[index]
                break            
        isActiveCourse = courseName in user.getActiveCourses()
        if isActiveCourse:
            user.getActiveCourses().remove(courseName)
        userSaveResult = user.update()
        profileSaveResult = profile.update()
        if not userSaveResult.success:
            return userSaveResult
        if not profileSaveResult.success:
            return profileSaveResult
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