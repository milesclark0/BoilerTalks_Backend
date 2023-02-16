from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import jwt_required
from http import HTTPStatus
#from functools import wraps
import app.queries.courses.courseQueries as queries
from app.models.Course import Course

bp = Blueprint('courses', __name__)

from app.blueprints.courses import routes