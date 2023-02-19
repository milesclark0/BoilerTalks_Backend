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
    
    response = jsonify({'data': {'accessToken': access_token, 'refreshToken': refresh_token, 'user': parse_json(res.data.formatDict())}, 'statusCode': HTTPStatus.OK, 'message': res.message})   
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
def registerAccount():
    #TODO: Add new user into database
    res = queries.register(request.json)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.UNAUTHORIZED, 'message': res.message})
    return jsonify(jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message}))


@bp.route(routePrefix + '/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    user = queries.getUserById(identity)
    if user.success and isinstance(user.data, User):
        user = user.data
    else:
        return jsonify({'data': None, 'statusCode': HTTPStatus.UNAUTHORIZED, 'message': user.message})
    
    response = jsonify({'data': {'accessToken': access_token, 'refreshToken': None, 'user': parse_json(user.formatDict())}, 'statusCode': HTTPStatus.OK, 'message': 'Refresh Successful'})
    set_access_cookies(response, access_token)
    return response


