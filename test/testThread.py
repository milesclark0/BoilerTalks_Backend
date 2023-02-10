import unittest, certifi
from app.models.Thread import Thread, ThreadMessages
from app.models.Course import Course
from pymongo import MongoClient
from bson import ObjectId
from config import Config

class ThreadTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        Thread.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Threads']
        Course.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Courses']
    #clear database before each test
    def setUp(self):
        Thread.collection.delete_many({})
        Course.collection.delete_many({})
    
    def test_from_dict_valid(self):
        #test only required fields
        thread_dict = {
            'name': 'Thread 1',
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
        }
        thread = Thread.fromDict(thread_dict)
        self.assertTrue(thread is not None)
        self.assertTrue(thread.getId() is None)

        #test all fields
        thread_dict = {
            'name': 'Thread 1',
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'numberOfPosts': 10,
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
        }
        thread = Thread.fromDict(thread_dict)
        self.assertTrue(thread is not None)
        self.assertTrue(thread.getId() == thread_dict['_id'])
        self.assertTrue(thread.getNumberOfPosts() == thread_dict['numberOfPosts'])
        self.assertTrue(thread.getName() == thread_dict['name'])
        self.assertTrue(thread.getCourseId() == thread_dict['courseId'])

    def test_from_dict_invalid(self):
        #test missing required fields
        thread_dict = {
            'name': 'Thread 1',
        }
        thread = Thread.fromDict(thread_dict)
        self.assertTrue(thread is None)

    def test_save_valid(self):
        #test only required fields
        #create course for thread
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())
        result = Course.collection.find_one({'_id': course.getId()})
        self.assertTrue(result is not None)


        thread = Thread('Thread 1', course.getId())
        result = thread.save()
        self.assertTrue(result.success)

        #check if thread was saved
        thread_db = Thread.collection.find_one({'_id': thread.getId()})
        self.assertTrue(thread_db is not None)

        #delete thread in order to use the same course for the next test
        Thread.collection.delete_one({'_id': thread.getId()})



        #test all fields
        thread_dict = {
            'name': 'Thread 1',
            'courseId': course.getId(),
            'numberOfPosts': 10,
            '_id': ObjectId('5f0b6a5a6c5a6f5d6c5a6f7d'),
        }
        thread = Thread.fromDict(thread_dict)
        self.assertTrue(thread is not None)
        result = thread.save()
        self.assertTrue(result.success)

        #check if thread was saved
        thread_db = Thread.collection.find_one({'_id': thread.getId()})
        self.assertTrue(thread_db is not None)

    def test_save_invalid(self):
        #test with invalid fields
        thread = Thread('', "")
        result = thread.save()
        self.assertFalse(result.success)

    def test_save_duplicate(self):
        #create course for thread
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())
        #test duplicate thread
        thread = Thread('Thread 1', course.getId())
        result = thread.save()
        self.assertTrue(result.success)

        #try to save duplicate thread
        result = thread.save()
        self.assertFalse(result.success)

    def test_update_valid(self):
        #create course for thread
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())

        #create thread
        thread = Thread('Thread 1', course.getId())
        result = thread.save()
        self.assertTrue(result.success)

        #update thread
        thread.setName('Thread 2')
        result = thread.update()
        self.assertTrue(result.success)

        #check if thread was updated
        thread_db = Thread.collection.find_one({'_id': thread.getId()})
        self.assertTrue(thread_db is not None)
        self.assertTrue(thread_db['name'] == thread.getName())

    def test_update_invalid(self):
        #update before saving
        thread = Thread('Thread 1', "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = thread.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == ThreadMessages.UPDATE_ERROR + ThreadMessages.NOT_FOUND)
    
    def test_delete_valid(self):
        #create course for thread
        course = Course('CS408', 'Software Engineering', 'user1', 'Computer Science', 'Spring 2020', None, ObjectId("5f0b6a5a6c5a6f5d6c5a6f5d"))
        Course.collection.insert_one(course.formatDict())

        #create thread
        thread = Thread('Thread 1', course.getId())
        result = thread.save()
        self.assertTrue(result.success)

        #delete thread
        result = thread.delete()
        self.assertTrue(result.success)

        #check if thread was deleted
        ret = Thread.collection.find_one({'_id': thread.getId()})
        self.assertTrue(ret is None)

    def test_delete_invalid(self):
        #delete before saving
        thread = Thread('Thread 1', "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = thread.delete()
        self.assertFalse(result.success)
        self.assertTrue(result.message == ThreadMessages.DELETE_ERROR + ThreadMessages.NOT_FOUND)

    def tearDown(self):
        Thread.collection.delete_many({})
        Course.collection.delete_many({})





