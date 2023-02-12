from app.blueprints.auth import *
routePrefix = '/auth'

@bp.route(routePrefix + '/login', methods=['GET'])
def login():
    #TODO: Implement login
    return jsonify({"Login": "Login"})


@bp.route(routePrefix + '/register', methods=['POST'])
def register():
    #TODO: Implement register
    # validate information fields
    return jsonify({"Register": "Register"})


