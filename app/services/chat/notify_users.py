from flask_socketio import emit, join_room
from app import presence_subscribers


def notify_presence_change(user_id, status):
    print("NOTIFY:", user_id, status)
    print("SUBSCRIBERS:", presence_subscribers)
    watchers = presence_subscribers.get(user_id, set())

    for watcher_id in watchers:
        emit(
            "presence_change",
            {"userId": user_id, "status": status},
            room=str(watcher_id),
        )
