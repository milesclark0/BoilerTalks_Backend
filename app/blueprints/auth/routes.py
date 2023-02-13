from app.blueprints.auth import *
routePrefix = '/auth'

@bp.route(routePrefix + '/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'data': None, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Credentials are missing!'})
    res = queries.login(auth.username, auth.password)
    if not res.success or not isinstance(res.data, User):
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.UNAUTHORIZED, 'message': res.message})
    
    # generate tokens
    access_token = create_access_token(identity = str(res.data.getId()))
    refresh_token = create_refresh_token(identity = str(res.data.getId()))
    
    return jsonify({'data': {'accessToken': access_token, 'refreshToken': refresh_token}, 'statusCode': HTTPStatus.OK, 'message': res.message})   

@bp.route(routePrefix + '/register', methods=['POST'])
@jwt_required()
def register():
    #TODO: Implement register
    #userInfo = queries.register(request.json)
    return jsonify({"data": "hello"})

@bp.route(routePrefix + '/registerCourses', methods=['GET'])
def registerCourses():
    #TODO: Retrieve courses
    courses = queries.getCourses()
    return jsonify({"data": courses})

@bp.route(routePrefix + '/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'data': {'accessToken': access_token}, 'statusCode': HTTPStatus.OK, 'message': 'Token refreshed'})


