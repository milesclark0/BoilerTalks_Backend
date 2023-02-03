from app.blueprints.auth import *

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('_auth')
        if not token:
            return jsonify({'data': None, 'statusCode': HTTPStatus.UNAUTHORIZED, 'message': 'Token is missing!'})
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')
        except Exception as e:
            print("Token Error: ", str(e))
            return jsonify({'data': None, 'statusCode': HTTPStatus.UNAUTHORIZED, 'message': str(e)})
        return f(*args, **kwargs)
    return decorated  
    