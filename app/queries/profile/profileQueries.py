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

def editProfile(bio: str, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error editing profile: user not found'
            return res

        if len(bio) > 500:
            res.message = 'error editing profile: bio over 500 chars'
            return res
        
        profile = Profile.fromDict(Profile.collection.find_one({ "username": username}))
        # if profile is None:
        #     res.message = 'error editing profile: profile not found'
        #     return res
        profile.setBio(bio)
        profileSaveResult = profile.update()
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

    



