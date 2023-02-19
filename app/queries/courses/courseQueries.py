from app.queries import *

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

def getCourse(name: str, semester:str):
    res = DBreturn()
    try:
        course = Course.collection.find_one({"name": name, "semester": semester})
        res.data = parse_json(course)
        res.success = True
        res.message = 'Successfully retrieved course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving course'
        res.data = str(e)
    return res
 
def subscribeToCourse(courseName: str, username: str):
    res = DBreturn()
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            res.success = False
            res.message = 'subscribe to course error: User not found'
            return res
        courses = Course.collection.find({"name": courseName})
        if courses is None:
            res.success = False
            res.message = 'subscribe to course error: Course not found'
            return res
        newCourses = courseName in user.getCourses()
        if newCourses:
            res.success = False
            res.message = 'subscribe to course error: Already subscribed to course'
            return res
        user.setCourses(user.getCourses() + [courseName])
        userSaveResult = user.update()
        if not userSaveResult.success:
            return userSaveResult
        # subscribe to every course (all semesters)
        for course in courses:
            print("saving course", course)
            course = Course.fromDict(course)
            if course is None:
                res.success = False
                res.message = "Unable to subscribe to course"
                return res
            course.setMemberCount(course.getMemberCount() + 1)
            courseSaveResult = course.update()
            if not courseSaveResult.success:
                return courseSaveResult
        res.success = True
        res.message = 'Successfully subscribed to course'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while subscribing to course'
        res.data = str(e)
        print(res.data)
    return res


