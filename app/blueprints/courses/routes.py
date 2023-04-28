from app.blueprints.courses import *

routePrefix = '/courses'

@bp.route(routePrefix + '/getAllCourses', methods=['GET'])
#@jwt_required()
def getAllCourses():
    res = queries.getAllCourses()
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getCourse/<id>', methods=['GET'])
@jwt_required()
def getCourse(id):
    res = DBreturn(False, 'No Course Provided', None)
    res = queries.getCourse(id)
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

@bp.route(routePrefix + '/getUserCoursesAndRooms/<username>', methods=['GET'])
@jwt_required()
def getUserCoursesAndRooms(username):
    res = DBreturn(False, 'No User Provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getUserCoursesAndRooms(username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getRoom/<roomId>', methods=['GET'])
@jwt_required()
def getRooms(roomId):
    res = DBreturn(False, 'No Room Provided', None)
    if roomId is None or roomId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getRoom(roomId)
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

@bp.route(routePrefix + '/getCourseManagement/<courseId>', methods=['GET'])
@jwt_required()
def getCourseAppeals(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getCourseManagementData(courseId)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/addAppeal/<courseId>', methods=['POST'])
@jwt_required()
def addAppealtoCourse(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    
    res = queries.addAppealforCourse(courseId)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateAppeal/<courseId>', methods=['POST'])
@jwt_required()
def updateAppealtoCourse(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    decision = request.json["decision"]
    res = queries.updateAppealforCourse(courseId, decision)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/banUser/<courseId>', methods=['POST'])
@jwt_required()
def banUser(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    user = request.json["user"]
    res = queries.banUserForCourse(courseId, user)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})