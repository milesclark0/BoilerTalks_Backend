from app.queries import *
from app.queries.courses.courseQueries import getUserCourses

def getProfile(username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error retrieving profile: user not found'
            return res
        profile = Profile.collection.find_one({ "username": username})
        if profile is None:
            res.message = 'error retrieving profile: profile not found'
            return res
        res.data = [parse_json(profile), parse_json(user)]
        res.success = True
        res.message = 'Successfully retrieved profile'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while retrieving profile'
        res.data = str(e)
    return res

def editProfile(data: object, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error editing profile: user not found'
            return res
        
        profile = Profile.fromDict(Profile.collection.find_one({ "username": username}))
        # if profile is None:
        #     res.message = 'error editing profile: profile not found'
        #     return res
        bio = data['bio']
        if bio is not None:
            profile.setBio(bio)
        classYear = data['classYear']
        if classYear is not None:
            profile.setClassYear(classYear)
        major = data['major']
        if major is not None:
            profile.setMajor(major)
        profileSaveResult = profile.update()
        print(profileSaveResult.message)
        if not profileSaveResult.success:
            return profileSaveResult
        res.success = True
        res.message = 'Successfully edited profile'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while editing profile'
        res.data = str(e)
        print(res.data)
    return res       

# def uploadProfilePicture(username: str, file):
#     res = DBreturn()
#     compressedFile = compress_file(file)
#     try:
#         userProfile = Profile.collection.find_one({"username": username})
#         if userProfile is None:
#             res.message = 'error uploading profile picture: user not found'
#             return res
#         userProfile = Profile.fromDict(userProfile)
#         userProfile.setProfilePicture(compressedFile)
#         profileSaveResult = userProfile.update()
#         if not profileSaveResult.success:
#             return profileSaveResult
#         #make sure to send back the non-compressed file
#         userProfile.setProfilePicture(file)
#         res.data = parse_json(userProfile.formatDict())
#         res.success = True
#         res.message = 'Successfully uploaded profile picture'
#     except Exception as e:
#         res.success = False
#         res.message = 'Error occurred while uploading profile picture'
#         res.data = str(e)
#     return res

def uploadProfilePictureAWS(username: str, file):
    res = getPresignedUrl(username)
    if not res.success:
        return res
    user = res.data
    res = uploadFileToS3(user, file)
    if not res.success:
        return res
    res = updateMessagesWithNewProfilePicture(user)
    return res

def updateMessagesWithNewProfilePicture(user: User):
    ret = DBreturn(False, 'Error updating messages with new profile picture', None)
    try:
        #get all courses the user is in
        res = getUserCourses(user.getUsername())
        print(res.message)
        if not res.success:
            return res
        courses = res.data
        msgCount = 0
        needUpdate = False
        #this checks all previous messages and updates the profile picture if it is different or if it is null
        for course in courses:
            for room in course['rooms']:
                for message in room['messages']:
                    if message['username'] == user.getUsername():
                        if message.get('profilePic', None) != user.getProfilePicture():
                            message['profilePic'] = user.getProfilePicture()
                            msgCount += 1
                            needUpdate = True
                room['courseId'] = room['courseId']['$oid']
                room['_id'] = room['_id']['$oid']
                roomObj = Room.fromDict(room)
                if needUpdate == True:
                    res = roomObj.update()
                    if not res.success:
                        return res
                    needUpdate = False
        ret.success = True
        ret.message = f'Successfully updated user profile picture in {msgCount} messages'

    except Exception as e:
        ret.message = str(e)
    return ret

def updateMessagesWithNewDisplayName(user: User):
    ret = DBreturn(False, 'Error updating messages with new display name', None)
    try:
        #get user profile
        profile = Profile.fromDict(Profile.collection.find_one({"username": user.getUsername()}))
        if not profile:
            return res
        
        #get all courses the user is in
        res = getUserCourses(user.getUsername())
        if not res.success:
            return res
        
        
        courses = res.data
        msgCount = 0
        needUpdate = False
        #this checks all previous messages and updates the profile picture if it is different or if it is null
        for course in courses:
            for room in course['rooms']:
                for message in room['messages']:
                    if message['username'] == user.getUsername():
                        #if the display name is null or empty, set it to the username
                        if not profile.getDisplayName():
                            profile.setDisplayName(user.getUsername())
                            res = profile.update()
                            if not res.success:
                                return res
                        if message.get('displayName', None) != profile.getDisplayName():
                            message['displayName'] = profile.getDisplayName()
                            msgCount += 1
                            needUpdate = True
                room['courseId'] = room['courseId']['$oid']
                room['_id'] = room['_id']['$oid']
                roomObj = Room.fromDict(room)
                if needUpdate == True:
                    res = roomObj.update()
                    if not res.success:
                        return res
                    needUpdate = False
        ret.success = True
        ret.message = f'Successfully updated user display name in {msgCount} messages'

    except Exception as e:
        ret.message = str(e)
    return ret

def updateNotificationPreference(username: str, notificationData: dict):
    res = DBreturn()
    try:
        profile = Profile.fromDict(Profile.collection.find_one({"username":  username}))
        if profile is None:
            res.message = 'get profile error: no profile found'
            return res
        # newNotificationData = {}
        notiPref = profile.getNotificationPreference()
        notiPref[notificationData["courseName"]] = notificationData["data"]
        # for courseNoti in notiPref:
        #     if courseNoti["roomId"] == notificationData["roomId"]:
        #         courseNoti = notificationData
        #     newNotificationData.append(courseNoti)
        # profile.setNotificationPreference(newNotificationData)
        saveNotificationPref = profile.update()
        if not saveNotificationPref.success:
            return saveNotificationPref
        res.success = True
        res.message = 'Successfully updated notification preference'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating notification preference'
        res.data = str(e)
    return res

def updateSeenNotification(username: str, notificationData: dict):
    res = DBreturn()
    try:
        profile = Profile.fromDict(Profile.collection.find_one({"username":  username}))
        if profile is None:
            res.message = 'get profile error: no profile found'
            return res
        profile.setSeenNotification(notificationData)
        saveSeenNotification = profile.update()
        if not saveSeenNotification.success:
            return saveSeenNotification
        res.success = True
        res.message = 'Successfully updated seen notification'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating seen notification'
        res.data = str(e)
    return res


def updateLastSeenMessage(username: str, seenMessageData: dict):
    res = DBreturn()
    try:
        profile = Profile.fromDict(Profile.collection.find_one({"username":  username}))
        if profile is None:
            res.message = 'get profile error: no profile found'
            return res
        # newMessageData = []
        # foundMessage = 0
        # for message in profile.getLastSeenMessage():
        #     if message["roomId"] == seenMessageData["roomId"]:
        #         foundMessage = 1
        #         message = seenMessageData
        #     newMessageData.append(message)
        # if not foundMessage:
        #     newMessageData.append(seenMessageData)
        # profile.setLastSeenMessage(newMessageData)
        lastSeenMessage = profile.getLastSeenMessage()
        lastSeenMessage[seenMessageData["roomId"]] = seenMessageData["data"]
        saveLastSeenMessage = profile.update()
        if not saveLastSeenMessage.success:
            return saveLastSeenMessage
        res.success = True
        res.message = 'Successfully updated last seen message'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while updating last seen message'
        res.data = str(e)
    return res