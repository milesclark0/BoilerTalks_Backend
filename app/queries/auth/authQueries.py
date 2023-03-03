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
    newUser = User.fromDict(userData)
    if newUser is None:
        return DBreturn(False, "Invalid User Data", None)
    newProfile = Profile(newUser.getUsername())
    if newProfile is None:
        return DBreturn(False, "Invalid Profile Data", None)
    res = User.save(newUser)
    if not res.success:
        return res
    resP = Profile.save(newProfile)
    if not resP.success:
        return resP
    return DBreturn(True, "Register Successful", res.data)

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
        profileData = Profile.collection.find_one({ "username": userData.getUsername()})
        if profileData is not None:
            profileData['profilePicture'] = decompress_file(profileData['profilePicture'])
    except Exception as e:
        return DBreturn(False, "Error occurred while retrieving user", str(e))
    if userData is None:
        return DBreturn(False, "User not found", None)
    return DBreturn(True, "User found", [userData, profileData])