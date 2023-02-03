from app import create_app, socketIo

flask_app = create_app(debug=True)

if __name__ == '__main__':
    socketIo.run(flask_app, debug=True)