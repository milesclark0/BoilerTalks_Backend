from app.blueprints.profile import *
routePrefix = '/profile'

@bp.route(routePrefix + '/getProfile/<username>', methods=['GET'])
@jwt_required()
def getProfile(username):
    res = DBreturn(True, 'No User Provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getProfile(username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/editProfile', methods=['POST'])
@jwt_required()
def editProfile():
    res = DBreturn(False, 'No Edits Performed', None)
    try:
        bio = request.json['bio']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.editProfile(bio, username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/uploadProfilePicture/<username>', methods=['POST'])
@jwt_required()
def uploadProfilePicture(username):
    res = DBreturn(False, 'No Image Uploaded', None)
    try:
        image = request.files['file'].read()
    except Exception as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.uploadProfilePicture(username, image)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})
