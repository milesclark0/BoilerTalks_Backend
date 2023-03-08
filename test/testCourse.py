import unittest, certifi
from app.models.Course import Course, CourseMessages
from app.models.CourseManagement import CourseManagement
from app.models.Thread import Thread
from app.models.Room import Room
from pymongo import MongoClient
from config import Config

class CourseTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        Course.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Courses']
        Thread.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Threads']
        Room.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Rooms']
        CourseManagement.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['CourseManagement']
    #clear database before each test
    def setUp(self):
        Course.collection.delete_many({})
        Thread.collection.delete_many({})
        Room.collection.delete_many({})
        CourseManagement.collection.delete_many({})


    def test_from_dict_valid(self):
        #test only required fields
        course_dict = {
            'name': 'CS408', 
            'description': 'Software Engineering', 
            'owner': 'user1', 
            'department': 'CS',
            'semester': 'Spring 2020' 
        }
        course = Course.fromDict(course_dict)
        self.assertTrue(course is not None)
        self.assertTrue(course.getId() is None)
        self.assertTrue(course.getCreationDate() is not None)
        self.assertTrue(course.getInstructor() is None)

        #test all fields
        course_dict = {
            'name': 'CS408',
            'description': 'Software Engineering',
            'owner': 'user1',
            'instructor': 'Dr. Smith',
            'department': 'CS',
            'semester': 'Spring 2020',
            'memberCount': 400,
            'userThread': '5f0b6a5a6c5a6f5d6c5a6f5d',
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'generalRoom': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'modRoom': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'creationDate': '2020-07-13 15:00:00'
        }
        course = Course.fromDict(course_dict)
        self.assertTrue(course is not None)
        self.assertTrue(course.getId() == course_dict['_id'])
        self.assertTrue(course.getCreationDate() == course_dict['creationDate'])

        #testing with required fields and optional fields
        course_dict = {
            'name': 'CS408',
            'description': 'Software Engineering',
            'owner': 'user1',
            'instructor': 'Dr. Smith',
            'department': 'CS',
            'semester': 'Spring 2020',
            'memberCount': 400,
            'userThread': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'generalRoom': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'modRoom': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'creationDate': '2020-07-13 15:00:00'
        }

        course = Course.fromDict(course_dict)
        self.assertTrue(course is not None)
        self.assertTrue(course.getId() is None)
        self.assertTrue(course.getCreationDate() == course_dict['creationDate'])

    def test_from_dict_invalid(self):
        #test missing required fields
        course_dict = {
            'description': 'Software Engineering',
            'owner': 'user1',
            'semester': 'Spring 2020'
        }
        course = Course.fromDict(course_dict)
        self.assertTrue(course is None)

    def test_save_valid(self):
        #create course, save course, and check if course is in database
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.save()
        self.assertTrue(result.success)

        #check if course is in database
        course_dict = Course.collection.find_one({'_id': course.getId()})
        self.assertTrue(course_dict is not None)

        #check if thread is in database
        thread_dict = Thread.collection.find_one({'_id': course.getUserThread()})
        self.assertTrue(thread_dict is not None)
        self.assertTrue(thread_dict['courseId'] == course.getId())

        #check if rooms are in database
        for room in course.getRooms():
            room_dict = Room.collection.find_one({'_id': room[1]})
            self.assertTrue(room_dict is not None)
            self.assertTrue(room_dict['courseId'] == course.getId())
        
        #check if mod room is in database
        room_dict = Room.collection.find_one({'_id': course.getModRoom()})
        self.assertTrue(room_dict is not None)
        self.assertTrue(room_dict['courseId'] == course.getId())

        #check if CourseManagement object is in database
        cm_dict = CourseManagement.collection.find_one({'courseId': course.getId()})
        self.assertTrue(cm_dict is not None)


    def test_save_invalid(self):
        #save with invalid fields
        course = Course('', '', '', '', '')
        result = course.save()
        self.assertFalse(result.success)
        self.assertTrue(CourseMessages.INVALID_FIELDS in result.message)
        
    def test_save_duplicate(self):
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.save()
        self.assertTrue(result.success)

        #save duplicate course
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.save()
        self.assertFalse(result.success)
        self.assertTrue(CourseMessages.COURSE_EXISTS in result.message)

        #save duplicate course with different different semester
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2021')
        result = course.save()
        self.assertTrue(result.success)

    def test_update_valid(self):
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.save()
        self.assertTrue(result.success)
        thread = course.getUserThread()
        room = course.getRooms()
        mod_room = course.getModRoom()

        #update course
        course.setInstructor('Dr. Smith')
        course.setMemberCount(400)
        result = course.update()
        self.assertTrue(result.success)
        
        #check if course is in database
        course_dict = Course.collection.find_one({'_id': course.getId()})
        self.assertTrue(course_dict is not None)
        self.assertTrue(course_dict['instructor'] == course.getInstructor())
        self.assertTrue(course_dict['memberCount'] == course.getMemberCount())

        #check thread and rooms are not changed
        self.assertTrue(course_dict['userThread'] == thread)
        self.assertTrue(course_dict['rooms'] == room)
        self.assertTrue(course_dict['modRoom'] == mod_room)

    def test_update_invalid(self):
        #update before saving
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == CourseMessages.UPDATE_ERROR + CourseMessages.COURSE_NOT_FOUND)

    def test_delete_valid(self):
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.save()
        self.assertTrue(result.success)

        #delete course
        result = course.delete()
        self.assertTrue(result.success)

        #check if course is in database
        course_dict = Course.collection.find_one({'_id': course.getId()})
        self.assertTrue(course_dict is None)

        #check if thread is in database
        thread_dict = Thread.collection.find_one({'_id': course.getUserThread()})
        self.assertTrue(thread_dict is None)

        #check if rooms are in database
        for room in course.getRooms():
            room_dict = Room.collection.find_one({'_id': room[1]})
            self.assertTrue(room_dict is None)
        room_dict = Room.collection.find_one({'_id': course.getModRoom()})
        self.assertTrue(room_dict is None)

    def test_delete_invalid(self):
        #delete before saving
        course = Course('CS408', 'Software Engineering', 'user1', 'CS', 'Spring 2020')
        result = course.delete()
        self.assertFalse(result.success)
        #will fail because of foreign keys set to None cannot be deleted
        self.assertTrue(result.message == CourseMessages.FOREIGN_KEYS_ERROR)

    #clear database after each test
    def tearDown(self):
        Course.collection.delete_many({})
        Thread.collection.delete_many({})
        Room.collection.delete_many({})
        CourseManagement.collection.delete_many({})
    