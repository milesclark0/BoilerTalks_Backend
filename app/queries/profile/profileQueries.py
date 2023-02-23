# queries relating to profile page
from app.queries import *

def showProfile(username):
    #TODO: Implement retrieving the profile info
    userData = User.fromDict(User.collection.find_one({ "username": username }))
    return "oops"

