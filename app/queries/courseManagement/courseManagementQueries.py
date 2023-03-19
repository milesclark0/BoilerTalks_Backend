from app.queries import *

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