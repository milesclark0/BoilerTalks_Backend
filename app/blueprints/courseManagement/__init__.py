from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import jwt_required
from http import HTTPStatus
#from functools import wraps
import app.queries.courseManagement.courseManagementQueries as queries
from app.models.CourseManagement import CourseManagement
from app.models.Course import Course
from app.models.Database import db, DBreturn, parse_json, ObjectId

bp = Blueprint('courseManagement', __name__)

from app.blueprints.courseManagement import routes