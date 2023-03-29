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
    
    print("Attempting to block " + toBlock + " on user " + username)
    res = queries.blockUser(toBlock, username)

    if not res.success:
        return jsonify({'data': res.data, 'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'message': res.message})
    return jsonify({'data': res.data, 'statusCode': HTTPStatus.OK, 'message': res.message})
