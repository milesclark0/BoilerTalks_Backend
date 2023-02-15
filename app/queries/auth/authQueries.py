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

def register(userData):
    newUser = User.fromDict(userData)
    response = User.save(newUser)
    return DBreturn(True, "Register Successful", response)

def getCourses():
    # Get all courses
    courses = Course.collection.find({}, {'_id': 0})
    return parse_json(courses)
