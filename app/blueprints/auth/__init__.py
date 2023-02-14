from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from http import HTTPStatus
#from functools import wraps
import app.queries.auth.authQueries as queries
from app.models.User import User

bp = Blueprint('auth', __name__)

from app.blueprints.auth import routes