from app.blueprints.courseManagement import *

routePrefix = '/courseManagement'

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
    courseAppeal = request.json
    res = queries.addAppealforCourse(courseId, courseAppeal)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateAppeal/<courseId>', methods=['POST'])
@jwt_required()
def updateAppealtoCourse(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    appeal = request.json
    res = queries.updateAppealforCourse(courseId, appeal)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/banUser/<courseId>', methods=['POST'])
@jwt_required()
def banUser(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    banData = request.json
    res = queries.banUserForCourse(courseId, banData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/warnUser/<courseId>', methods=['POST'])
@jwt_required()
def warnUser(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    warnData = request.json
    res = queries.warnUserForCourse(courseId, warnData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/updateWarnList/<courseId>', methods=['POST'])
@jwt_required()
def updateWarnUser(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    warnData = request.json
    res = queries.updateWarnListForCourse(courseId, warnData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})