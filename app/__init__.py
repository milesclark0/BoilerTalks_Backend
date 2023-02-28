from flask_jwt_extended import JWTManager
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from config import Config
import logging

socketIo = SocketIO(cors_allowed_origins="http://127.0.0.1:5173")
jwt = JWTManager()


# Configure logging for the application
logger = logging.getLogger(__name__)
formatter = logging.Formatter('\n%(filename)s:%(lineno)d: %(message)s')
_consoleHandler = logging.StreamHandler()
_consoleHandler.setFormatter(formatter)
logger.addHandler(_consoleHandler)

# Set the logging level for the application here: DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL
logger.setLevel(logging.WARNING)

def create_app(config_class=Config, debug=int(Config.FLASK_DEBUG)):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = debug
    CORS(app, supports_credentials=True)

    # Initialize Flask extensions here

    # Register blueprints here
    from app.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.courses import bp as courses_bp
    app.register_blueprint(courses_bp)

    from app.blueprints.profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    
    from app.blueprints.messaging import bp as messaging_bp
    from app.blueprints.messaging import namespace as messaging_namespace
    app.register_blueprint(messaging_bp)

    socketIo.on_namespace(messaging_namespace.MyCustomNamespace('/chat'))
    socketIo.init_app(app)
    jwt.init_app(app)

    return app