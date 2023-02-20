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
    res = DBreturn(None, 'No Course Provided', True)
    res = queries.getCourse(name)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/getUserCourses/<username>', methods=['GET'])
@jwt_required()
def getUserCourses(username):
    res = DBreturn(None, 'No User Provided', True)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.getUserCourses(username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})


@bp.route(routePrefix + '/subscribeToCourses', methods=['POST'])
@jwt_required()
def subscribeToCourse():
    res = DBreturn(None, 'No new Courses Provided', True)
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
    res = DBreturn(None, 'No course provided', True)
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
    res = DBreturn(None, 'No new Courses Provided', True)
    try:
        courseId = request.json['course']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'Courses and username are required'})
    res = queries.unsubscribeFromCourse(courseId, username)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})