from flask_socketio import emit
from app import presence_subscribers


def notify_presence_change(user_id, mode, status):
    identity = f"{user_id}:{mode}"

    print("NOTIFY PRESENCE")
    print("identity:", identity)
    print("status:", status)

    watchers = presence_subscribers.get(identity, set())

    print("WATCHERS:", watchers)

    for watcher_identity in watchers:
        print("EMITTING TO:", watcher_identity)
        emit(
            "presence_change",
            {
                "identity": identity,
                "status": status,
            },
            room=watcher_identity,
        )
