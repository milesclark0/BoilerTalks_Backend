import unittest, certifi
from app.models.CourseManagement import CourseManagement, CourseManagementMessages
from pymongo import MongoClient
from config import Config

class CourseManagementTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        CourseManagement.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Users']
    #clear database before each test
    def setUp(self):
        CourseManagement.collection.delete_many({})

    def test_from_dict_valid(self):
        #test only required fields
        cm_dict = {
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
        }
        cm = CourseManagement.fromDict(cm_dict)
        self.assertTrue(cm is not None)
        self.assertTrue(cm.getId() is None)
        self.assertTrue(cm.getCreationDate() is not None)

        #test all fields
        cm_dict = {
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'creationDate': '2020-07-13 15:00:00',
            'rules': [],
            'announcements': [],
            'appeals': [],
            'requests': [],
            'bannedUsers': [],
            'moderators': [],

        }
        cm = CourseManagement.fromDict(cm_dict)
        self.assertTrue(cm is not None)
        self.assertTrue(cm.getId() == cm_dict['_id'])
        self.assertTrue(cm.getCreationDate() == cm_dict['creationDate'])

    def test_from_dict_invalid(self):
        #test missing required fields
        cm_dict = {
            'rules': [],
            'announcements': [],
        }
        cm = CourseManagement.fromDict(cm_dict)
        self.assertTrue(cm is None)

    def test_save_valid(self):
        #create a new cm, save it, then check if it's in database
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')
        result = cm.save()
        self.assertTrue(result.success)

        #check if cm is in database
        cm_dict = CourseManagement.collection.find_one({'_id': cm.getId()})
        self.assertTrue(cm_dict is not None)

        #check all fields
        cm_dict = {
            'courseId': '5f0b6a5a6c5a6f5d6c5a6f5c',
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'creationDate': '2020-07-13 15:00:00',
            'rules': [],
            'announcements': [],
            'appeals': [],
            'requests': [],
            'bannedUsers': [],
            'moderators': [],
        }
        cm = CourseManagement.fromDict(cm_dict)
        result = cm.save()
        self.assertTrue(result.success)

        #check if cm is in database
        cm_dict = CourseManagement.collection.find_one({'_id': cm.getId()})
        self.assertTrue(cm_dict is not None)

    def test_save_invalid(self):
        #save with invalid fields
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d', rules='not a list')
        result = cm.save()
        self.assertFalse(result.success)
        self.assertTrue(CourseManagementMessages.INVALID_FIELDS in result.message)

    def test_save_duplicate(self):
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')
        result = cm.save()
        self.assertTrue(result.success)

        #save duplicate cm
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')     
        result = cm.save()
        self.assertFalse(result.success)
        self.assertTrue(CourseManagementMessages.CM_EXISTS in result.message)

    def test_update_valid(self):
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')
        result = cm.save()
        self.assertTrue(result.success)

        #update profile
        cm.setRules(['No spamming'])
        result = cm.update()
        self.assertTrue(result.success)
        
        #check if cm is in database
        cm_dict = CourseManagement.collection.find_one({'_id': cm.getId()})
        self.assertTrue(cm_dict is not None)
        self.assertTrue(cm_dict['rules'] == cm.getRules())

    def test_update_invalid(self):
        #update before saving
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')
        result = cm.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == CourseManagementMessages.UPDATE_ERROR + CourseManagementMessages.NOT_FOUND)

    def test_delete_valid(self):
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')      
        result = cm.save()
        self.assertTrue(result.success)

        #delete profile
        result = cm.delete()
        self.assertTrue(result.success)

        #check if cm is in database
        cm_dict = CourseManagement.collection.find_one({'_id': cm.getId()})
        self.assertTrue(cm_dict is None)

    def test_delete_invalid(self):
        #delete before saving
        cm = CourseManagement(courseId='5f0b6a5a6c5a6f5d6c5a6f5d')
        result = cm.delete()
        self.assertFalse(result.success)
        self.assertTrue(result.message == CourseManagementMessages.DELETE_ERROR + CourseManagementMessages.NOT_FOUND)

    #clear database after each test
    def tearDown(self):
        CourseManagement.collection.delete_many({})
