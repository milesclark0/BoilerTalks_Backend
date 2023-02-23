from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity
from http import HTTPStatus
#from functools import wraps
import app.queries.profile.profileQueries as queries
from app.models.User import User

bp = Blueprint('profile', __name__)

from app.blueprints.profile import routes