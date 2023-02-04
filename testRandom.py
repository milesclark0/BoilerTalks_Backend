from app.models.User import User
import datetime


user = User('username', 'password', 'email@purdue.edu', 'firstName', 'lastName', [''], 'profilePicture', ['blockedUsers'])
userDict = {"username": "username", "password": "password", "email": "email", "firstName": "firstName", "lastName": "lastName", "courses": ["courses"], "profilePicture": "profilePicture", "blockedUsers": ["blockedUsers"]}
user2 = User.fromDict(userDict)

print(user)
print(user.validateFields(False))

