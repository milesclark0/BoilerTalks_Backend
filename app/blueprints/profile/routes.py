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
    res = queries.uploadProfilePictureAWS(username, image)
    if not res.success:
        return jsonify({'data': None, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': None, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/updateNotification/<username>', methods=['POST'])
@jwt_required()
def updateNotification(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    notificationData = request.json
    res = queries.updateNotification(username, notificationData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateLastSeenMessage/<username>', methods=['POST'])
@jwt_required()
def updateLastMessage(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    seenData = request.json
    res = queries.updateLastSeenMessage(username, seenData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateLastSeenAppeal/<username>', methods=['POST'])
@jwt_required()
def updateLastAppeal(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    appealData = request.json
    res = queries.updateLastSeenAppeal(username, appealData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateLastSeenReport/<username>', methods=['POST'])
@jwt_required()
def updateLastReport(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    reportData = request.json
    res = queries.updateLastSeenReport(username, reportData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})
