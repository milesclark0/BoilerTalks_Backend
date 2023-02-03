from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS
from http import HTTPStatus
from flask_socketio import SocketIO, emit, Namespace
import jwt, datetime
from functools import wraps
import app.queries.auth.authQueries as queries

bp = Blueprint('auth', __name__)

from app.blueprints.auth import routes