from app.queries import *

def getProfile(username: str):
    res = DBreturn()
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            res.message = 'error retrieving profile: user not found'
            return res
        # search based on user object, eliminate credentials from result
        profile = Profile.collection.find({ "user": user, {"user.password": 0, "user.email": 0}})
        res.data = parse_json(profile)
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
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            res.message = 'error editting profile: user not found'
            return res

        if len(bio) > 500:
            res.message = 'error editting profile: bio over 500 chars'
            return res
        
        profile = Profile.fromDict(Profile.collection.find({ "user": user}))
        profile.setBio(bio)
        profileSaveResult = profile.update()
        if not profileSaveResult.success:
            return profileSaveResult
        res.success = True
        res.message = 'Successfully editted profile'
    except Exception as e:
        res.success = False
        res.message = 'Error occurred while editting profile'
        res.data = str(e)
        print(res.data)
    return res       


        


