# This file will handle all the queries related to authentication
from app.queries import *

# all queries related to authentication
# should return a DBreturn object
def login(username, password):
    #TODO: Implement login
    try:
        userData = User.fromDict(User.collection.find_one({ "username": username }))
    except Exception as e:
        return DBreturn(False, "Error occured while logging in", str(e))
    if userData is None:
        return DBreturn(False, "User not found", None)
    if userData.getPassword() != User.hashPassword(password):
        return DBreturn(False, "Invalid username or password", None)
    return DBreturn(True, "Login Successful", userData)

def register(userData):
    print(userData)
    newUser = User.fromDict(userData)
    res = User.save(newUser)
    print(res.data)
    if not res.success:
        return DBreturn(False, "Register Unsuccessful", res.data)
    return DBreturn(True, "Register Successful", res)

def getCourses():
    # Get all courses
    courses = Course.collection.find({}, {'_id': 0})
    return parse_json(courses)
