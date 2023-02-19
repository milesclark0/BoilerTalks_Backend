from app.blueprints.courses import *

routePrefix = '/courses'

@bp.route(routePrefix + '/getAllCourses', methods=['GET'])
#@jwt_required()
def getAllCourses():
    res = queries.getAllCourses()
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
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': 'CourseId and username are required'})
    for courseId in courseIdArray:
        print(courseId, "in subscribeToCourse")
        res = queries.subscribeToCourse(courseId, username)
        if not res.success:
            return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})