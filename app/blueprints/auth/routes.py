from app.blueprints.auth import *

@bp.route('/login', methods=['GET'])
def login():
    #TODO: Implement login
    return "Login"


@bp.route('/register', methods=['POST'])
def register():
    #TODO: Implement register
    return "Register"


