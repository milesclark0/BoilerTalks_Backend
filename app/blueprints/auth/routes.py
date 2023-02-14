from app.blueprints.auth import *
routePrefix = '/auth'

@bp.route(routePrefix + '/login', methods=['POST'])
def login():
    #TODO: Implement login
    user = queries.login(request.json["username"], request.json["password"])
    return jsonify({"data": user})


@bp.route(routePrefix + '/register', methods=['POST'])
def registerInfo():
    #TODO: check user information
    userInfo = queries.registerInfo(request.json)
    return jsonify({"data": userInfo})

@bp.route(routePrefix + '/register', methods=['PUT'])
def registerAccount():
    #TODO: Add new user into database
    return jsonify({"data": "data"})

@bp.route(routePrefix + '/register', methods=['GET'])
def registerCourses():
    #TODO: Retrieve courses
    courses = queries.getCourses()
    return jsonify({"data": courses})


