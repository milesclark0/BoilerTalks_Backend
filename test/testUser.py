import unittest, certifi
from app.models.User import User, UserMessages
from pymongo import MongoClient
from config import Config






class UserTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        User.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Users']

    #clear database before each test
    def setUp(self):
        User.collection.delete_many({})
    

    def test_save_valid(self):
        #create user, save user
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS 40800'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()

        #check if method returned success
        self.assertTrue(result.success)

        #check if user was saved
        found = User.collection.find_one({"username": user.getUsername()})
        self.assertTrue(found != None)

    def test_save_invalid(self):
        #create user with some invalid fields
        user = User('us', 'password', 'email@iu.edu', 'f', 'l', [''], [''], 'invalidURL', [''])
        result = user.save()
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.SAVE_ERROR + UserMessages.FIELDS_INVALID)

        #check for all errors
        self.assertTrue(UserMessages.USERNAME_LENGTH in result.data)

        self.assertTrue(UserMessages.PASS_NUMBER in result.data)
        self.assertTrue(UserMessages.PASS_UPPER in result.data)
        self.assertTrue(UserMessages.PASS_SPECIAL in result.data)

        self.assertTrue(UserMessages.EMAIL_INVALID in result.data)

        self.assertTrue(UserMessages.FIRSTNAME_LENGTH in result.data)
        self.assertTrue(UserMessages.LASTNAME_LENGTH in result.data)

        self.assertTrue(UserMessages.COURSE_NULL in result.data)
        self.assertTrue(UserMessages.ACTIVE_COURSE_NULL in result.data)
        self.assertTrue(UserMessages.PROFILE_PICTURE_INVALID_LINK in result.data)
        self.assertTrue(UserMessages.BLOCKED_USER_NULL in result.data)

    def test_save_duplicate(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS 40800'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        user2 = User.fromDict(user.formatDict())
        user3 = User.fromDict(user.formatDict())
        result = user.save()
        self.assertTrue(result.success)

        # save user again
        result = user2.save()

        # should not allow duplicate usernames
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.USERNAME_TAKEN)

        # create user with same email, save user
        user3.setUsername('user3')
        result = user3.save()

        # should not allow duplicate emails
        self.assertFalse(result.success) 
        self.assertTrue(result.message == UserMessages.EMAIL_TAKEN)

    def test_update_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        # change user's fields
        user.setFirstName('newFirstName')

        # update user
        result = user.update()
        self.assertTrue(result.success)

        # check if user was updated
        found = User.collection.find_one({"username": user.getUsername()})
        self.assertTrue(found != None)

        #check that password normally caught by validator is not due to update and not save
        user.setPassword('JHDCEJJFKKNDJU59')
        result = user.update()
        self.assertTrue(result.success)

    def test_update_invalid(self):
        user = User('user has not been saved', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
   
        # update user
        result = user.update()

        # should not allow update of user that has not been saved
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.UPDATE_ERROR + UserMessages.NOT_FOUND)

    def test_delete_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        # delete user
        result = user.delete()
        self.assertTrue(result.success)

        # check if user was deleted
        found = User.collection.find_one({"username": user.getUsername()})
        self.assertTrue(found == None)

    def test_delete_invalid(self):
        user = User('user has not been saved', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], ['CS 40800'], 'https:/imgur.com/abcd.jpg', ['user2'])

        # delete user
        result = user.delete()

        # should not allow delete of user that has not been saved
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.DELETE_ERROR + UserMessages.NOT_FOUND)

    def test_from_dict_valid(self):
        # testing with only required fields
        user1_dict = {
            "username": "user1",
            "password": "Password1!",
            "email": 'email@purdue.edu',
            "firstName": "firstName",
            "lastName": "lastName",
        }

        user1 = User.fromDict(user1_dict)
        self.assertTrue(user1 is not None)
        self.assertTrue(user1.getId() is None)
        # creation date should be set when user is if not provided
        self.assertTrue(user1.getCreationDate() is not None)

        # testing with all fields
        user2_dict = {
            "_id": "5f5f5f5f5f5f5f5f5f5f5f5f",
            "username": "user1",
            "password": "Password1!",
            "email": 'email@purdue.edu',
            "firstName": "firstName",
            "lastName": "lastName",
            "courses": ['CS 40800'],
            "activeCourses": ['CS40800'],
            "profilePicture": 'https:/imgur.com/abcd.jpg',
            "blockedUsers": ['user2'],
            "creationDate": "2020-09-09 00:00:00",
        }

        user2 = User.fromDict(user2_dict)
        self.assertTrue(user2 is not None)
        self.assertTrue(user2.getId() == user2_dict["_id"])
        self.assertTrue(user2.getCreationDate() == user2_dict["creationDate"])
        #testing with required fields and optional fields
        user3_dict = {
            "username": "user1",
            "password": "Password1!",
            "email": 'email@purdue.edu',
            "firstName": "firstName",
            "lastName": "lastName",
            "courses": ['CS 40800'],
            "activeCourses": ['CS 40800'],
            "profilePicture": 'https:/imgur.com/abcd',
            "blockedUsers": ['user2'],
            "creationDate": "2020-09-09 00:00:00",
        }

        user3 = User.fromDict(user3_dict)
        self.assertTrue(user3 is not None)
        self.assertTrue(user3.getId() is None)
        self.assertTrue(user3.getCreationDate() is not None)

    def test_from_dict_invalid(self):
        # testing with missing required fields
        user1_dict = {
            "username": "user1",
            "password": "Password1!",
            "email": 'email@purdue.edu',
        }

        user1 = User.fromDict(user1_dict)
        self.assertTrue(user1 is None)


    # clear database after each test
    def tearDown(self):
        User.collection.delete_many({})

if __name__ == '__main__':
    unittest.main()
    
    

