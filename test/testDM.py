import unittest, certifi
from app.models.DM import DM, DmMessages
from app.models.User import User
from pymongo import MongoClient
from config import Config

class DMTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        DM.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['DMs']
        User.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Users']

    #clear database before each test
    def setUp(self):
        DM.collection.delete_many({})
        User.collection.delete_many({})

    def test_from_dict_valid(self):
        #test only required fields
        dm_dict = {
            'users': ["user1", "user2"],
        }
        dm = DM.fromDict(dm_dict)
        self.assertTrue(dm is not None)
        self.assertTrue(dm.getId() is None)
        dm_dict['users'].sort()
        self.assertTrue(dm.getUsers() == dm_dict['users'])

        #test all fields
        dm_dict = {
            'users': ["user1", "user2"],
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'messages': [{
                'username': 'user1',
                'message': 'Hello',
                'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z"
        }
        dm = DM.fromDict(dm_dict)
        self.assertTrue(dm is not None)
        self.assertTrue(dm.getId() == dm_dict['_id'])
        dm_dict['users'].sort()
        self.assertTrue(dm.getUsers() == dm_dict['users'])

    def test_from_dict_invalid(self):
        #test missing required fields
        dm_dict = {
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'messages': [{
                'username': 'user1',
                'message': 'Hello',
                'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z"
        }
        dm = DM.fromDict(dm_dict)
        self.assertTrue(dm is None)

    def test_save_valid(self):
        #create 2 users for dm
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        user2 = User("user2", "Password1!", 'email2@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user1'])
        result = user2.save()
        self.assertTrue(result.success)


        #test only required fields
        dm = DM(["user1", "user2"])
        result = dm.save()
        self.assertTrue(result.success)

        #check that the dm was saved to the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is not None)
        dm.delete()

        #test all fields
        dm_dict = {
            'users': ["user1", "user2"],
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'messages': [{
                'username': 'user1',
                'message': 'Hello',
                'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z"
        }
        dm = DM.fromDict(dm_dict)
        result = dm.save()
        self.assertTrue(result.success)

        #check that the dm was saved to the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is not None)

    def test_save_invalid(self):
        #test with invalid users
        dm_dict = {
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'users': ["user1", ""],
            'messages': [{
                'username': 'user1',
                'message': 'Hello',
                'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z"
        }
        dm = DM.fromDict(dm_dict)
        result = dm.save()
        self.assertFalse(result.success)

    def test_save_duplicate(self):
        #create 2 users for dm
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        user2 = User("user2", "Password1!", 'email2@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user1'])
        result = user2.save()
        self.assertTrue(result.success)

        dm = DM(["user1", "user2"])
        result = dm.save()
        self.assertTrue(result.success)

        #check that the dm was saved to the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is not None)

        #try to save the same dm again
        result = dm.save()
        self.assertFalse(result.success)


    def test_update_valid(self):
        #create 2 users for dm
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        user2 = User("user2", "Password1!", 'email2@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user1'])
        result = user2.save()
        self.assertTrue(result.success)

        dm = DM(["user1", "user2"])
        result = dm.save()
        self.assertTrue(result.success)

        dm.setMessages([{
            'username': 'user1',
            'message': 'Hello',
            'timestamp': '2020-07-20T20:20:39.299Z'
        }])
        result = dm.update()
        self.assertTrue(result.success)

        #check that the dm was updated in the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is not None)
        self.assertTrue(result['messages'] == dm.getMessages())

    def test_update_invalid(self):
        #update a dm that has not been saved
        dm = DM(["user1", "user2"])
        result = dm.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == DmMessages.UPDATE_ERROR + DmMessages.NOT_FOUND)


    def test_delete_valid(self):
        #create 2 users for dm
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        user2 = User("user2", "Password1!", 'email2@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user1'])
        result = user2.save()
        self.assertTrue(result.success)

        dm = DM(["user1", "user2"])
        result = dm.save()
        self.assertTrue(result.success)

        #check that the dm was saved to the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is not None)

        result = dm.delete()
        self.assertTrue(result.success)

        #check that the dm was deleted from the database
        result = DM.collection.find_one({'_id': dm.getId()})
        self.assertTrue(result is None)

    def test_delete_invalid(self):
        #delete a dm that has not been saved
        dm = DM(["user1", "user2"])
        result = dm.delete()
        self.assertFalse(result.success)
        self.assertTrue(result.message == DmMessages.DELETE_ERROR + DmMessages.NOT_FOUND)
    
        

    def tearDown(self) -> None:
        DM.collection.delete_many({})
        User.collection.delete_many({})





    
