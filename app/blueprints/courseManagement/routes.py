from app.blueprints.courses import *

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