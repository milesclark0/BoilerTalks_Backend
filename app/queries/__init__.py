from app.models.Database import db, DBreturn, parse_json, ObjectId
from app.models.User import User
from app.models.Course import Course
from app.models.DM import DM
from app.models.Post import Post
from app.models.Room import Room
from app.models.Thread import Thread
from app.models.Room import Room
from app.models.Profile import Profile
import gzip
from io import BytesIO

def compress_file(file_data):
    out = BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb') as f:
        f.write(file_data)
    return out.getvalue()

def decompress_file(file_data):
    out = BytesIO()
    with gzip.GzipFile(fileobj=BytesIO(file_data), mode='rb') as f:
        out.write(f.read())
    return out.getvalue()
