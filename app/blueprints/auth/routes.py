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
    
    response = jsonify({'data': {'accessToken': access_token, 'refreshToken': refresh_token}, 'statusCode': HTTPStatus.OK, 'message': res.message})   
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response

@bp.route(routePrefix + '/logout', methods=['GET'])
@jwt_required()
def logout():
    response = jsonify({'data': None, 'statusCode': HTTPStatus.OK, 'message': 'Logout Successful'})
    unset_jwt_cookies(response) 
    return response

@bp.route(routePrefix + '/register', methods=['POST'])
@jwt_required()
def registerAccount():
    #TODO: Add new user into database
    return jsonify({"data": "data"})

@bp.route('/courses/getAllCourses', methods=['GET'])
def selectableCourses():
    # returns courses to select in register
    courses = queries.getCourses()
    return jsonify({"data": courses})


@bp.route(routePrefix + '/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    response =  jsonify({'data': {'accessToken': access_token}, 'statusCode': HTTPStatus.OK, 'message': 'Token refreshed'})
    set_access_cookies(response, access_token)
    return response


