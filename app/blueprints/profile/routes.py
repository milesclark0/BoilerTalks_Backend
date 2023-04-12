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

@bp.route(routePrefix + '/editProfile/<username>', methods=['POST'])
@jwt_required()
def editProfile(username):
    res = DBreturn(False, 'No Edits Performed', None)
    try:
        data = request.json
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.editProfile(data, username)
    if not res.success:
        res.message = str(res.data)
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


@bp.route(routePrefix + '/updateNotificationPreference/<username>', methods=['POST'])
@jwt_required()
def updateNotificationPreference(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    notificationData = request.json
    res = queries.updateNotificationPreference(username, notificationData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateSeenNotification/<username>', methods=['POST'])
@jwt_required()
def updateSeenNotification(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    notificationData = request.json["notifications"]
    res = queries.updateSeenNotification(username, notificationData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateLastSeenMessage/<username>', methods=['POST'])
@jwt_required()
def updateLastSeenMessage(username):
    res = DBreturn(False, 'No user provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    messageData = request.json
    res = queries.updateLastSeenMessage(username, messageData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})
