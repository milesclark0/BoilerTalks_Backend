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
    try:
        newUser = User.fromDict(userData)
    except Exception as e:
        return DBreturn(False, "Error occured while creating new user fields", str(e))
    try:
        res = User.save(newUser)
    except Exception as e:
        return DBreturn(False, "Error occured while saving user", str(e))
    if not res.success:
        return DBreturn(False, "Register Unsuccessful", res.data)
    return DBreturn(True, "Register Successful", res)

def getUserById(id):
    try:
        userData = User.fromDict(User.collection.find_one({ "_id": ObjectId(id)}))
    except Exception as e:
        return DBreturn(False, "Error occurred while retrieving user", str(e))
    if userData is None:
        return DBreturn(False, "User not found", None)
    return DBreturn(True, "User found", userData)