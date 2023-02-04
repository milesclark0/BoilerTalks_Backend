import unittest, certifi
from app.models.User import User, UserMessages
import datetime
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
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()

        #check if method returned success
        self.assertTrue(result.success)

        #check if user was saved
        found = User.collection.find_one({"username": user.getUsername()})
        self.assertTrue(found != None)

    def test_save_invalid(self):
        #create user invalid password, save user
        user = User('use', 'password', 'email@iu.edu', 'f', 'l', [''], 'invalidURL', [''])
        result = user.save()
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.SAVE_ERROR + UserMessages.FIELDS_INVALID)

        #check for all errors
        self.assertTrue(UserMessages.USERNAME_LENGTH in result.data[0])

        self.assertTrue(UserMessages.PASS_NUMBER in result.data[1])
        self.assertTrue(UserMessages.PASS_UPPER in result.data[1])
        self.assertTrue(UserMessages.PASS_SPECIAL in result.data[1])

        self.assertTrue(UserMessages.EMAIL_INVALID in result.data[2])

        self.assertTrue(UserMessages.FIRSTNAME_LENGTH in result.data[3])
        self.assertTrue(UserMessages.LASTNAME_LENGTH in result.data[4])

        self.assertTrue(UserMessages.COURSE_NULL in result.data[5])
        self.assertTrue(UserMessages.PROFILE_PICTURE_INVALID in result.data[6])
        self.assertTrue(UserMessages.BLOCKED_USER_NULL in result.data[7])

    def test_save_duplicate(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        #create user with same username, save user
        user2 = user
        result = user2.save()

        # should not allow duplicate usernames
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.USERNAME_TAKEN)

        # create user with same email, save user
        user2.setUsername('user2')
        result = user2.save()

        # should not allow duplicate emails
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.EMAIL_TAKEN)

    def test_update_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
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
        user = User('user has not been saved', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
   
        # update user
        result = user.update()

        # should not allow update of user that has not been saved
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.UPDATE_ERROR + UserMessages.NOT_FOUND)

    def test_delete_valid(self):
        user = User('user1', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])
        result = user.save()
        self.assertTrue(result.success)

        # delete user
        result = user.delete()
        self.assertTrue(result.success)

        # check if user was deleted
        found = User.collection.find_one({"username": user.getUsername()})
        self.assertTrue(found == None)

    def test_delete_invalid(self):
        user = User('user has not been saved', 'Password1!', 'email@purdue.edu', 'firstName', 'lastName', ['CS408'], 'https:/imgur.com/abcd.jpg', ['user2'])

        # delete user
        result = user.delete()

        # should not allow delete of user that has not been saved
        self.assertFalse(result.success)
        self.assertTrue(result.message == UserMessages.DELETE_ERROR + UserMessages.NOT_FOUND)
    
    

    # clear database after each test
    def tearDown(self):
        User.collection.delete_many({})

    



if __name__ == '__main__':
    unittest.main()
    
    

