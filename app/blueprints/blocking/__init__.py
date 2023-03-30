from flask import request, jsonify, Blueprint, current_app
from flask_jwt_extended import create_access_token, jwt_required, create_refresh_token, get_jwt_identity
from http import HTTPStatus
#from functools import wraps
import app.queries.blocking.blockingQueries as queries
from app.models.User import User
from app.models.Database import db, DBreturn, parse_json, ObjectId
import boto3
import os, binascii
from dotenv import load_dotenv

bp = Blueprint('blocking', __name__)

from app.blueprints.blocking import routes