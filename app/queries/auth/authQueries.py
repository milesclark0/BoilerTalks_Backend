# This file will handle all the queries related to authentication
from app.queries import *

def login(username, password):
    #TODO: Implement login
    userData = User.collection.find_one({ "username": username })
    if not userData or userData.password != password: 
        return "Error"
    return "Success"

def registerInfo(jsonData):
    #TODO: Implement register
    # print(User.validatePassword(jsonData))
    return "Success"

def getCourses():
    #TODO: Get courses
    courses = Course.collection.find({}, {'_id': 0})
    return json.loads(json_util.dumps(courses))
