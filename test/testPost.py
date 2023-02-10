import unittest, certifi
from app.models.Post import Post, PostMessages
from pymongo import MongoClient
from config import Config

class PostTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        ca = certifi.where()
        Post.collection = MongoClient(Config.DB_CONN_STR, tlsCAFile=ca)[Config.DB_NAME_TEST]['Posts']

    #clear database before each test
    def setUp(self):
        Post.collection.delete_many({})

    def test_from_dict_valid(self):
        #test only required fields
        post_dict = {
            'threadId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'author': 'user1',
            'content': 'Hello',
            'title': 'Title',
        }
        post = Post.fromDict(post_dict)
        self.assertTrue(post is not None)
        self.assertTrue(post.getId() is None)

        #test all fields
        post_dict = {
            'threadId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'author': 'user1',
            'content': 'Hello',
            'title': 'Title',
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'tags': ['tag1', 'tag2'],
            'comments': [{
            'username': 'user1',
            'message': 'Hello',
            'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z",
            'acceptedAnswer': {"username": "user1", "message": "Hello", "timestamp": "2020-07-20T20:20:39.299Z"},
            'isResolved': True
        }
        post = Post.fromDict(post_dict)
        self.assertTrue(post is not None)
        self.assertTrue(post.getId() == post_dict['_id'])
    
    def test_from_dict_invalid(self):
        #test missing required fields
        post_dict = {
            'author': 'user1',
            'content': 'Hello',
            'title': 'Title',
        }
        post = Post.fromDict(post_dict)
        self.assertTrue(post is None)

    def test_save_valid(self):
        # test only required fields
        post_dict = {
            'threadId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'author': 'user1',
            'content': 'Hello',
            'title': 'Title',
        }
        post = Post.fromDict(post_dict)
        result = post.save()
        self.assertTrue(result.success)

        #check that post was saved
        found = Post.collection.find_one({'_id': post.getId()})
        self.assertTrue(found is not None)
        post.delete()

        #test all fields
        post_dict = {
            'threadId': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'author': 'user1',
            'content': 'Hello',
            'title': 'Title',
            '_id': '5f0b6a5a6c5a6f5d6c5a6f5d',
            'tags': ['tag1', 'tag2'],
            'comments': [{
            'username': 'user1',
            'message': 'Hello',
            'timestamp': '2020-07-20T20:20:39.299Z'
            }],
            "creationDate": "2020-07-20T20:20:39.299Z",
            'acceptedAnswer': {"username": "user1", "message": "Hello", "timestamp": "2020-07-20T20:20:39.299Z"},
            'isResolved': True
        }
        post = Post.fromDict(post_dict)
        result = post.save()
        self.assertTrue(result.success)

        #check that post was saved
        found = Post.collection.find_one({'_id': post.getId()})
        self.assertTrue(found is not None)

    def test_save_invalid(self):
        #test invalid fields 
        post = Post("","","","")
        result = post.save()
        self.assertFalse(result.success)
        self.assertTrue(result.message == PostMessages.SAVE_ERROR + PostMessages.INVALID_FIELDS)

    def test_save_duplicate(self):
        #test duplicate post
        post = Post("author", "content", "title", "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = post.save()
        self.assertTrue(result.success)

        result = post.save()
        self.assertFalse(result.success)
        self.assertTrue(result.message == PostMessages.SAVE_ERROR + PostMessages.POST_EXISTS)


    def test_update_valid(self):
        post = Post("author", "content", "title", "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = post.save()
        self.assertTrue(result.success)

        post.setContent("content2")
        
        result = post.update()
        self.assertTrue(result.success)

        #check that post was updated
        found = Post.collection.find_one({'_id': post.getId()})
        self.assertTrue(found is not None)
        self.assertTrue(found['author'] == post.getAuthor())
        self.assertTrue(found['content'] == post.getContent())

    def test_update_invalid(self):
        #test update before save
        post = Post("author", "content", "title", "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = post.update()
        self.assertFalse(result.success)
        self.assertTrue(result.message == PostMessages.UPDATE_ERROR + PostMessages.NOT_FOUND)

    def test_delete_valid(self):
        post = Post("author", "content", "title", "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = post.save()
        self.assertTrue(result.success)

        #check that post was saved
        found = Post.collection.find_one({'_id': post.getId()})
        self.assertTrue(found is not None)


        result = post.delete()
        self.assertTrue(result.success)

        #check that post was deleted
        found = Post.collection.find_one({'_id': post.getId()})
        self.assertTrue(found is None)

    def test_delete_invalid(self):
        #test delete before save
        post = Post("author", "content", "title", "5f0b6a5a6c5a6f5d6c5a6f5d")
        result = post.delete()
        self.assertFalse(result.success)
        self.assertTrue(result.message == PostMessages.DELETE_ERROR + PostMessages.NOT_FOUND)

    def tearDown(self):
        Post.collection.delete_many({})


