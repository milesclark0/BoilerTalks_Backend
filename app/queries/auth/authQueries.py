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
        newProfile = Profile(newUser.getUsername())
    except Exception as e:
        return DBreturn(False, "Error occured while creating new user fields", str(e))
    try:
        res = User.save(newUser)
        resP = Profile.save(newProfile)
    except Exception as e:
        return DBreturn(False, "Error occured while saving user", str(e))
    if not res.success:
        return DBreturn(False, "Register Unsuccessful", res.data)
    if not resP.success:
        return DBreturn(False, "Profile Creation Unsuccessful", res.data)
    return DBreturn(True, "Register Successful", res)

def resetPassword(username, password):
    try:
        userData = User.fromDict(User.collection.find_one({ "username": username }))
    except Exception as e:
        return DBreturn(False, "Error occured while resetting password", str(e))
    if userData is None:
        return DBreturn(False, "User not found", None)
    else:
        userData.setPassword(password)
    try:
        res = userData.update()
    except Exception as e:
        return DBreturn(False, "Error occured while saving user", str(e))
    if not res.success:
        return DBreturn(False, "Password Reset Unsuccessful", res.data)
    return DBreturn(True, "Password Reset Successful", res)

def getUserById(id):
    try:
        userData = User.fromDict(User.collection.find_one({ "_id": ObjectId(id)}))
    except Exception as e:
        return DBreturn(False, "Error occurred while retrieving user", str(e))
    if userData is None:
        return DBreturn(False, "User not found", None)
    return DBreturn(True, "User found", userData)