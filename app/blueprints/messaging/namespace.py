from app.blueprints.messaging import *

# Tracks all rooms joined by a client
rooms = {str: [str]}


class MyCustomNamespace(Namespace):
    def on_connect(self):
        print('Client connected')

    def leave_all_rooms(self, sid):
        for room in rooms.get(sid, []):
            if room != sid:
                print(f"Disconnecting client: Leaving room {room}")
                leave_room(room)
                foundRoom = queries.getRoom(room)
                res = queries.leaveRoom(foundRoom, None, sid)
                if res.success:
                    #emit("send_message", res.message, to=room)
                    print("Client left room")
                else:
                    print(res.message)
                rooms.get(sid).remove(room)
        print("All rooms left")


    def on_disconnect(self):
        print('Client disconnected')
        sid = request.sid
        #leave all rooms
        print(f"All rooms joined by {sid} ", rooms.get(sid))
        self.leave_all_rooms(sid)
        return "Client disconnected"

    def on_send_message(self, data):
        message = data['message']
        print(f"sending message {message} to room {data['roomID']}")
        roomId = data['roomID']

        room = queries.getRoom(roomId)
        res = queries.sendMessage(room, message)
        if res.success:
            emit("send_message", message, broadcast=True, to=roomId)
        else:
            print(res.message)
               
    def on_join(self, data):
        roomID = data['roomID']
        username = data['username']
        profilePic = data['profilePic']
        sid = request.sid
        print(f"Joining roomID: {roomID}")
        print(f"sid: {sid}")
        
        #leave all rooms before joining a new one
        self.leave_all_rooms(sid)
        foundRoom = queries.getRoom(roomID)
        res = queries.joinRoom(foundRoom, username, sid, profilePic)
        if (isinstance(rooms.get(sid), list)):
            rooms[sid].append(roomID)
        else:
            rooms[sid] = [roomID]
        join_room(roomID)
        print(f"All rooms joined by {sid} ", rooms.get(sid))
        if res.success:
            #emit("send_message", f"---{username} has joined the room.---", to=roomID)
            print(res.message)
        else:
            print(res.message)
        return {'data': res.__dict__}

    def on_leave(self, data):
        roomID = data['roomID']
        username = data['username']
        sid = request.sid
        print(f"Leaving roomID: {roomID}")
        print(f"sid: {sid}")

        foundRoom = queries.getRoom(roomID)
        res = queries.leaveRoom(foundRoom, username, sid)

        if (isinstance(rooms.get(sid), list)):
            rooms[sid].remove(roomID)
        else:
            rooms[sid] = []
        leave_room(roomID)
        if res.success:
            #emit("send_message", f"---{username} has left the room.---", to=roomID)
            print(res.message)
        return {'data': res.__dict__}