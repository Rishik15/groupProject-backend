from app.sockets.login.login import register_login_socket_events


def register_socket_events(socketio):
    register_login_socket_events(socketio)
