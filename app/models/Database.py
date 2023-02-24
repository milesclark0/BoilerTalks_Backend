from pymongo import MongoClient
from config import Config
import json
from bson import json_util, ObjectId

# connect to the database
client = MongoClient(Config.DB_CONN_STR)

# get the database
db = client[Config.DB_NAME]



# class returned by database methods and queries
class DBreturn:
    success: bool
    message: str
    data: object

    def __init__(self, success: bool = False, message: str = "", data: object = None):
        self.success = success
        self.message = message
        self.data = data

    def __str__(self):
        string = self.__dict__
        if self.success:
            if (isinstance(self.data, dict)):
                string['data'] = string['data'].__dict__
            else :
                string['data'] = str(self.data)
        return str(string)

# method to parse a database object into a json object
def parse_json(data):
    return json.loads(json_util.dumps(data))
