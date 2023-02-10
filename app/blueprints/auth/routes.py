from app.blueprints.auth import *
routePrefix = '/auth'

@bp.route(routePrefix + '/login', methods=['GET'])
def login():
    #TODO: Implement login
    return "Login"


@bp.route(routePrefix + '/register', methods=['GET'])
def register():
    #TODO: Implement register
    return "Register"


