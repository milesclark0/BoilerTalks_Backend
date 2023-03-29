from app.queries import *

def blockUser(toBlock: str, username: str):
    res = DBreturn()
    try:
        user = User.collection.find_one({"username": username})
        if user is None:
            res.message = 'error blocking user: blocker user not found'
            return res
        
        toBlock = User.collection.find_one({"username": toBlock})
        if toBlock is None:
            res.message = 'error blocking user: user to block not found'
            return res
        
        userDict = User.fromDict(user)
        blockDict = User.fromDict(toBlock)

        if userDict.getBlockedUsers().__contains__(toBlock):
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