# This file will handle all the queries related to authentication
from app.queries import *

# all queries related to authentication
# should return a DBreturn object
def login(username, password):
    #TODO: Implement login
    userData = User.fromDict(User.collection.find_one({ "username": username }))
    if userData is None:
        return DBreturn(False, "User not found", None)
    if userData.getPassword() != User.hashPassword(password):
        return DBreturn(False, "Invalid username or password", None)
    return DBreturn(True, "Login Successful", userData)

def registerInfo(jsonData):
    #TODO: Implement register
    # print(User.validatePassword(jsonData))
    return "Success"

def getCourses():
    #TODO: Get courses
    courses = Course.collection.find({}, {'_id': 0})
    return parse_json(courses)
