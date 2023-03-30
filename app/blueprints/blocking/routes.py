from app.blueprints.blocking import *
routePrefix = '/blocking'

@bp.route(routePrefix + '/blockUser', methods=['POST'])
@jwt_required()
def blockUser():
    res = DBreturn(True, 'Block not performed', None)
    try:
        toBlock = request.json['toBlock']
        username = request.json['username']
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    
    res = queries.blockUser(toBlock, username)

    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})

@bp.route(routePrefix + '/unblockUser', methods=['POST'])
@jwt_required()
def unblockUser():
    res = DBreturn(True, 'Unblock not performed', None)
    try:
        toUnblock = request.json['toUnblock']
        username = request.json['username']
        print("Backend trying to unblock " + toUnblock)
    except KeyError as e:
        return jsonify({'data': str(e), 'statusCode': HTTPStatus.BAD_REQUEST, 'message': res.message})
    
    res = queries.unblockUser(toUnblock, username)
    print("successful unblock?")

    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})