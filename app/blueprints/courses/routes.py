from app.blueprints.courses import *

routePrefix = '/courses'

@bp.route(routePrefix + '/getAllCourses', methods=['GET'])
#@jwt_required()
def getAllCourses():
    res = queries.getAllCourses()
    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})