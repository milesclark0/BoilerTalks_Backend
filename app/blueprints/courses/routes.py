from app.blueprints.courses import *

routePrefix = '/courses'

@bp.route(routePrefix + '/getAllCourses', methods=['GET'])
#@jwt_required()
def getAllCourses():
    res = queries.getAllCourses()
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getCourse/<name>', methods=['GET'])
@jwt_required()
def getCourseByName(name):
    res = DBreturn(False, 'No Course Provided', None)
    res = queries.getCourse(name)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/getUserCourses/<username>', methods=['GET'])
@jwt_required()
def getUserCourses(username):
    res = DBreturn(False, 'No User Provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getUserCourses(username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/subscribeToCourses', methods=['POST'])
@jwt_required()
def subscribeToCourse():
    res = DBreturn(False, 'No new Courses Provided', None)
    try:
        courseIdArray = request.json['courses']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Courses and username are required'})
    for courseId in courseIdArray:
        res = queries.subscribeToCourse(courseId, username)
        if not res.success:
            return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/setActiveCourse', methods=['POST'])
@jwt_required()
def setCourseActive():
    res = DBreturn(False, 'No new Courses Provided', None)
    try:
        courseName = request.json['courseName']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Course and username required'})
    res = queries.setCourseActive(courseName, username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/unsubscribeFromCourse', methods=['POST'])
@jwt_required()
def unsubscribeFromCourse():
    res = DBreturn(False, 'No new Courses Provided', None)
    try:
        courseName = request.json['courseName']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Courses and username are required'})
    res = queries.unsubscribeFromCourse(courseName, username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/addRoomToCourse', methods=['POST'])
@jwt_required()
def addRoomToCourse():
    res = DBreturn(False, 'No new Courses Provided', None)
    try:
        courseName = request.json['courseName']
        roomName = request.json['roomName']
        print(courseName, roomName)
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Courses and room name are required'})
    res = queries.addRoomToCourse(courseName, roomName)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getCourseUsers/<courseName>', methods=['GET'])
@jwt_required()
def getCourseUsers(courseName):
    res = DBreturn(False, 'No Course Provided', None)
    if courseName is None or courseName == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getCourseUsers(courseName)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getCourseAppeals/<courseName>', methods=['GET'])
@jwt_required()
def getCourseAppeals(courseName):
    res = DBreturn(False, 'No Course Provided', None)
    if courseName is None or courseName == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getAppealsforCourse(courseName)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getBannedUsers/<courseName>', methods=['GET'])
@jwt_required()
def getBannedUsers(courseName):
    res = DBreturn(False, 'No Course Provided', None)
    if courseName is None or courseName == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getBannedUsersforCourse(courseName)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})