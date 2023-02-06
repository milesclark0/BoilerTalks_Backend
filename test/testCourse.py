import unittest, certifi
from app.models.Course import Course, CourseMessages
from pymongo import MongoClient
from config import Config

class CourseTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        Course.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Courses']

    #clear database before each test
    def setUp(self):
        Course.collection.delete_many({})


    def test_from_dict_valid(self):
        #test only required fields
        course_dict = {
            'name': 'CS408', 
            'description': 'Software Engineering', 
            'owner': 'user1', 
            'instructor': 'Dr. Smith', 
            'department': 'Computer Science',
            'semester': 'Spring 2020' 
        }
        course = Course.fromDict(course_dict)
        self.assertTrue(course is not None)

        #test all fields
        course_dict = {
            'name': 'CS408',
            'description': 'Software Engineering',
            'owner': 'user1',
            'instructor': 'Dr. Smith',
            'department': 'Computer Science',
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





    #clear database after each test
    def tearDown(self):
        Course.collection.delete_many({})
    