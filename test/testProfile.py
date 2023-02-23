import unittest, certifi
from app.models.User import User
from app.models.Profile import Profile
from pymongo import MongoClient
from config import Config

class ProfileTests(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        User.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Users']
        Profile.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Profiles']
    #clear database before each test
    def setUp(self):
        User.collection.delete_many({})
        Profile.collection.delete_many({})

    def test_from_dict_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS 40800'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        user.save()
        #test only required fields
        profile_dict = {
            'username': user._username, 
        }
        profile = Profile.fromDict(profile_dict)
        self.assertTrue(profile is not None)
        self.assertTrue(profile.getId() is None)
        self.assertTrue(profile.getCreationDate() is not None)

        #test all fields
        profile_dict = {
            'username': user._username,
            'bio': 'this is my bio hip hip hooray',
            'modThreads': ['5f0b6a5a6c5a6f5d6c5a6f5d'],
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'creationDate': '2020-07-13 15:00:00'
        }
        profile = Profile.fromDict(profile_dict)
        self.assertTrue(profile is not None)
        self.assertTrue(profile.getId() == profile_dict['_id'])
        self.assertTrue(profile.getCreationDate() == profile_dict['creationDate'])

    def test_from_dict_invalid(self):
        #test missing required fields
        profile_dict = {
            'bio': 'this shouldnt exist',
            'modThreads': ['5f0b6a5a6c5a6f5d6c5a6f5d']
        }
        profile = Profile.fromDict(profile_dict)
        self.assertTrue(profile is None)

    def test_save_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS 40800'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        user.save()
        #create a new profile, save it, then check if it's in database
        profile = Profile(user._username, 'bio here')
        result = profile.save()
        self.assertTrue(result.success, result.message)

        #check if profile is in database
        profile_dict = Profile.collection.find_one({'_id': profile.getId()})
        self.assertTrue(profile_dict is not None)
