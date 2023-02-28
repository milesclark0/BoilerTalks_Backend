from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS
from http import HTTPStatus
from flask_socketio import SocketIO, emit, Namespace, join_room, leave_room
import jwt, datetime
from functools import wraps
import app.queries.messaging.messageQueries as queries

bp = Blueprint('sockets', __name__)

from app.blueprints.messaging import namespace