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

@bp.route(routePrefix + '/addCourseMods/<username>/<courseId>', methods=['POST'])
@jwt_required()
def addCourseMods(username, courseId):
    res = DBreturn(False, 'No username Provided', None)
    if username is None or username == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    res = queries.addCourseMod(username, courseId)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getPrevBannedUsers/<courseId>', methods=['GET'])
@jwt_required()
def getPrevBannedUsers(courseId):
    res = DBreturn(False, 'No course Provided', None)
    res = queries.getPrevBannedUsers(courseId)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getPrevWarnedUsers/<courseId>', methods=['GET'])
@jwt_required()
def getPrevWarnedUsers(courseId):
    res = DBreturn(False, 'No course Provided', None)
    res = queries.getPrevWarnedUsers(courseId)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/getCourseMods/<courseId>', methods=['GET'])
@jwt_required()
def getCourseMods( courseId):
    res = DBreturn(False, 'No username Provided', None)
    res = queries.getCourseMods(courseId)
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

@bp.route(routePrefix + '/updateCourseRules/<courseId>', methods=['POST'])
@jwt_required()
def updateCourseRules(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    rules = request.json['rules']
    res = queries.updateCourseRules(courseId, rules)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/addReport/<courseId>', methods=['POST'])
@jwt_required()
def addReport(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    reportData = request.json
    res = queries.addReport(courseId, reportData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/removeReport/<courseId>', methods=['POST'])
@jwt_required()
def removeReport(courseId):
    res = DBreturn(False, 'No Course Provided', None)
    if courseId is None or courseId == '':
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    reportData = request.json
    res = queries.removeReport(courseId, reportData)
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})
