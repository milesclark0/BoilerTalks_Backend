from app.models.Database import db, DBreturn, parse_json, ObjectId
from app.models.User import User
from app.models.Course import Course
from app.models.DM import DM
from app.models.Post import Post
from app.models.Room import Room
from app.models.Thread import Thread
from app.models.Room import Room
from app.models.Profile import Profile
from app.models.CourseManagement import CourseManagement
from dotenv import load_dotenv
import boto3, os, datetime

# Load environment variables from .env file which contains AWS credentials
load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION_NAME')
)

# get a presigned url for uploading an image to S3
def getPresignedUrl(username: str):
    bucketUrl = 'https://boilertalks-profile-images.s3.amazonaws.com/'
    ret = DBreturn(False, 'Error generating presigned url', None)
    try:
        user = User.fromDict(User.collection.find_one({"username": username}))
        if user is None:
            ret.message = 'User not found'
            return ret
        
        if user.getProfilePicture().startswith(bucketUrl):
            ret.message = 'User already has a profile picture'
            ret.success = True
            ret.data = user
            return ret
        
        img_name = str(user.getId()) + '.jpg'
        url = bucketUrl + img_name
        user.setProfilePicture(url)
        ret = user.update()
    except Exception as e:
        ret.message = str(e)
        print(ret.message)
        return ret
    return ret

def uploadFileToS3(user: User, file):
    ret = DBreturn(False, 'Error uploading file to S3', None)
    try:
        img_name = str(user.getId()) + '.jpg'
        s3.put_object(Bucket=os.environ.get('AWS_BUCKET_NAME'), Key=img_name, Body=file)
        ret.success = True
        ret.message = 'Successfully uploaded file to S3'
    except Exception as e:
        ret.message = str(e)
        print(ret.message)
    return ret


