import unittest, certifi
from app.models.Room import Room, RoomMessages
from app.models.Course import Course
from pymongo import MongoClient
from bson import ObjectId
from config import Config

class RoomTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        Room.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Rooms']
        Course.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Courses']
    #clear database before each test
    def setUp(self):
        Room.collection.delete_many({})
        Course.collection.delete_many({})
    
    def test_from_dict_valid(self):
        #test only required fields
        room_dict = {
            'name': 'Room 1',
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
        }
        room = Room.fromDict(room_dict)
        self.assertTrue(room is not None)
        self.assertTrue(room.getId() is None)

        #test all fields
        room_dict = {
            'name': 'Room 1',
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'connected': [{"sid": "1", "username": "user1"}, {"sid": "2", "username": "user2"}],
            "messages": [{"username": "user1", "message": "message1", "timeSent": "2020-07-20 12:00:00"}, {"username": "user2", "message": "message2", "timeSent": "2020-07-20 12:00:10"}],
            "_id": "5f0b6a5a6c5a6f5d6c5a6f5d"
        }
        room = Room.fromDict(room_dict)
        self.assertTrue(room is not None)
        self.assertTrue(room.getId() == room_dict['_id'])
        self.assertTrue(room.getName() == room_dict['name'])
        self.assertTrue(room.getCourseId() == room_dict['courseId'])
        self.assertTrue(room.getConnected() == room_dict['connected'])
        self.assertTrue(room.getMessages() == room_dict['messages'])

    def test_from_dict_invalid(self):
        #test missing required fields
        room_dict = {
            'name': 'Room 1',
        }
        room = Room.fromDict(room_dict)
        self.assertTrue(room is None)

    def test_save_valid(self):
        #test only required fields
        #create course for room
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())
        result = Course.collection.find_one({'_id': course.getId()})
        self.assertTrue(result is not None)


        room = Room('Room 1', course.getId())
        result = room.save()
        self.assertTrue(result.success)

        #check if room was saved
        room_db = Room.collection.find_one({'_id': room.getId()})
        self.assertTrue(room_db is not None)

        #delete room
        Room.collection.delete_one({'_id': room.getId()})



        #test all fields
        room_dict = {
            "_id": "5f0b6a5a6c5a6f5d6c5a6f5d",
            'name': 'Room 1',
            'courseId': course.getId(),
            'connected': [{"sid": "1", "username": "user1"}, {"sid": "2", "username": "user2"}],
            "messages": [{"username": "user1", "message": "message1", "timeSent": "2020-07-20 12:00:00"}, {"username": "user2", "message": "message2", "timeSent": "2020-07-20 12:00:10"}],
        }
        room = Room.fromDict(room_dict)
        self.assertTrue(room is not None)
        result = room.save()
        self.assertTrue(result.success)

        #check if room was saved
        room_db = Room.collection.find_one({'_id': room.getId()})
        self.assertTrue(room_db is not None)

    def test_save_invalid(self):
        #test with invalid fields
        room = Room('', "")
        result = room.save()
        self.assertFalse(result.success)

    def test_save_duplicate(self):
        #create course for room
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())
        #test duplicate room
        room = Room('Room 1', course.getId())
        result = room.save()
        self.assertTrue(result.success)

        #try to save duplicate room
        result = room.save()
        self.assertFalse(result.success)

    def test_update_valid(self):
        #create course for room
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())

        #create room
        room = Room('Room 1', course.getId())
        result = room.save()
        self.assertTrue(result.success)

        #update room
        room.setName('Room 2')
        result = room.update()
        self.assertTrue(result.success)

        #check if room was updated
        room_db = Room.collection.find_one({'_id': room.getId()})
        self.assertTrue(room_db is not None)
        self.assertTrue(room_db['name'] == room.getName())

    def test_update_invalid(self):
        #update before saving
        room = Room('Room 1', "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = room.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == RoomMessages.UPDATE_ERROR + RoomMessages.NOT_FOUND)
    
    def test_delete_valid(self):
        #create course for room
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())

        #create room
        room = Room('Room 1', course.getId())
        result = room.save()
        self.assertTrue(result.success)

        #delete room
        result = room.delete()
        self.assertTrue(result.success)

        #check if room was deleted
        ret = Room.collection.find_one({'_id': room.getId()})
        self.assertTrue(ret is None)

    def test_delete_invalid(self):
        #delete before saving
        room = Room('Room 1', "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = room.delete()
        self.assertFalse(result.success)
        self.assertTrue(result.message == RoomMessages.DELETE_ERROR + RoomMessages.NOT_FOUND)

    def tearDown(self):
        Room.collection.delete_many({})
        Course.collection.delete_many({})





