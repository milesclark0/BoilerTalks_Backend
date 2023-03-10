from app.queries import *



def getRoom(roomId):
    if roomId is None or roomId == "":
        return None
    try:
        room = Room.collection.find_one({"_id": ObjectId(roomId)})
        return room
    except Exception as e:
        print(e)
        return None
    
def leaveRoom(room, username, sid):
    res = DBreturn()
    if (username is None or username == "") and (sid is None or sid == ""):
        res.message = "Username or sid is required"
        return res
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    foundUser = next((member for member in room.getConnected() if member['username'] == username or member['sid'] == sid), None)
    if foundUser is None:
        res.message = "User not found in room"
        return res
    room.getConnected().remove(foundUser)
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully left room"
    return res
    
def joinRoom(room, username, sid, profilePic):
    res = DBreturn()
    if (username is None or username == "") and (sid is None or sid == ""):
        res.message = "Username or sid is required"
        return res
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    foundUser = next((member for member in room.getConnected() if member['username'] == username or member['sid'] == sid), None)
    if foundUser is None:
        room.getConnected().append({"username": username, "sid": sid, "profilePic": profilePic})
    else:
        #safe guard if user is already in room, but has a different sid
        foundUser['sid'] = sid
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully joined room"
    return res

def sendMessage(room, message):
    res = DBreturn()
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    room.getMessages().append(message)
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully sent message"
    return res

    
