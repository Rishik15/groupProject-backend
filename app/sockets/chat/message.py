from flask_socketio import emit, join_room
from flask import session, request
from app import chat_online_users, presence_subscribers
from app.services.chat.notify_users import notify_presence_change


def register_message_socket_events(socketio):
    def send_message():
        pass

    def recieve_message():
        pass

