from app.queries import *

def blockUser(toBlock: str, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error blocking user: blocker user not found'
            return res
        
        blockTarget = User.collection.find_one({"username": toBlock})
        if blockTarget is None:
            res.message = 'error blocking user: user to block not found'
            return res
        
        userDict = User.fromDict(user)
        blockDict = User.fromDict(blockTarget)

        if toBlock in userDict.getBlockedUsers():
            res.message = 'error blocking user: user already blocked'
            return res
        
        blockedUserList = userDict.getBlockedUsers()
        blockedUserList.append(blockDict.getUsername())

        print(blockedUserList)

        userDict.setBlockedUsers(blockedUserList)
        userSaveResult = userDict.update()
        if not userSaveResult.success:
            return userSaveResult
        res.success = True
        res.message = 'Successfully blocked user'

    except Exception as e:
        res.success = False
        res.message = 'Error occurred while blocking user'
        res.data = str(e)
        print(res.data)
    return res  

def unblockUser(toUnblock: str, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error blocking user: unblocker user not found'
            return res
        
        unblockTarget = User.collection.find_one({"username": toUnblock})
        if unblockTarget is None:
            res.message = 'error blocking user: user to unblock not found'
            return res
        
        userDict = User.fromDict(user)
        unblockDict = User.fromDict(unblockTarget)

        if toUnblock not in userDict.getBlockedUsers():
            res.message = 'error blocking user: user already unblocked'
            return res
        
        print(userDict.getUsername())

        blockedUserList = userDict.getBlockedUsers()
        blockedUserList.remove(unblockDict.getUsername())

        print(blockedUserList)

        userDict.setBlockedUsers(blockedUserList)
        userSaveResult = userDict.update()
        if not userSaveResult.success:
            return userSaveResult
        res.success = True
        res.message = 'Successfully unblocked user'

    except Exception as e:
        res.success = False
        res.message = 'Error occurred while unblocking user'
        res.data = str(e)
        print(res.data)
    return res  