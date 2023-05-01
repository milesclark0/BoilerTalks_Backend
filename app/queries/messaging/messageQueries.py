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
    
def joinRoom(room, username, sid, profilePic, displayName):
    res = DBreturn(True, "Successfully joined room", None)
    if (username is None or username == "") and (sid is None or sid == ""):
        res.message = "Username or sid is required"
        return res
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    foundUser = next((member for member in room.getConnected() if member['username'] == username or member['sid'] == sid), None)
    if foundUser is None:
        room.getConnected().append({"username": username, "sid": sid, "profilePic": profilePic, "displayName": displayName})
    else:
        #safe guard if user is already in room, but has a different sid
        foundUser['sid'] = sid
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    return res

def sendMessage(room, message):
    res = DBreturn()
    room = Room.fromDict(room)
    senderProfile = Profile.collection.find_one({"username": message["username"]})
    if senderProfile is None:
        res.message = "Sender profile not found"
        return res
    senderProfile = Profile.fromDict(senderProfile)
    message['displayName'] = senderProfile.getDisplayName()
    if room is None:
        res.message = "Room not found"
        return res
    room.getMessages().append(message)
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    courseName = Course.collection.find_one({"_id": room.getCourseId()})
    courseName = courseName["name"]
    profiles = Profile.collection.find({})
    for profile in profiles:
        profile = Profile.fromDict(profile)
        if profile.getUsername() != message["username"] or profile.getDisplayName() != message["username"]:
            notiPref = profile.getNotificationPreference()
            if courseName in notiPref:
                if notiPref[courseName]["messages"]:
                    # get lastSeenMessages of room to see if it has been viewed
                    lastSeenMessage =  profile.getLastSeenMessage()
                    lastSeenMessageRoom = lastSeenMessage.get(str(room.getId()), None)
                    if lastSeenMessageRoom is not None:
                        if lastSeenMessageRoom["message"]["timeSent"] != message["timeSent"]:
                            profile.getNotification().append({"courseName": courseName, "notification": "new message in " + str(room.getId()), "date": datetime.datetime.utcnow()})
                            saveProfile = profile.update()
                            if not saveProfile.success:
                                return saveProfile
    res.success = True
    res.message = "Successfully sent message"
    return res

def editMessage(room, message, index):
    res = DBreturn()
    room = Room.fromDict(room)
    senderProfile = Profile.collection.find_one({"username": message["username"]})
    if senderProfile is None:
        res.message = "Sender profile not found"
        return res
    senderProfile = Profile.fromDict(senderProfile)
    message['displayName'] = senderProfile.getDisplayName()
    if room is None:
        res.message = "Room not found"
        return res
    room.getMessages()[index] = message
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully sent message"
    return res

def deleteMessage(room, message):
    res = DBreturn(False, "Failed to delete message", None)
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    messages = room.getMessages()
    #find message with matching timeSent and username to remove
    newMessages = []
    for msg in messages:
        if msg["timeSent"] != message["timeSent"] or msg["username"] != message["username"]:
            newMessages.append(msg)
    room.setMessages(newMessages)
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully removed message"
    return res

def updateMessage(room, index, reaction, username, displayName):
    res = DBreturn()
    room = Room.fromDict(room)
    if room is None:
        res.message = "Room not found"
        return res
    messages = room.getMessages()
    msg = messages[index]
    current_reactions = msg.get("reactions", None)
    if current_reactions is None:
        msg["reactions"] = [{ "username": username, "reaction": reaction, "displayName": displayName}]
    else:
        msg["reactions"].append({ "username": username, "reaction": reaction, "displayName": displayName})
    roomSaveResult = room.update()
    if not roomSaveResult.success:
        return roomSaveResult
    res.success = True
    res.message = "Successfully sent message"
    return res
