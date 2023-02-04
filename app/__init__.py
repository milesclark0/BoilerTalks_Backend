
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

from config import Config

socketIo = SocketIO(cors_allowed_origins="http://localhost:5173")

def create_app(config_class=Config, debug=int(Config.FLASK_DEBUG)):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = debug
    CORS(app, supports_credentials=True)

    # Initialize Flask extensions here

    # Register blueprints here
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    
    socketIo.init_app(app)

    return app