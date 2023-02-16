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
        res.message = 'Error occured while retrieving all courses'
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
        res.message = 'Error occured while retrieving course'
        res.data = str(e)
    return res
