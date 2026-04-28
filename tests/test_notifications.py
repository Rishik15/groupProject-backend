from unittest.mock import patch
import json

SVC = "app.services.notifications.get_Notifications"
ROUTE = "app.routes.notifications.getNotifications"

FAKE_ROW = {
    "id": 1, "user_id": 2, "type": "coach_session", "mode": "client",
    "conversation_id": None, "reference_id": 1,
    "metadata": json.dumps({"route": "/client/workouts", "event_id": 1}),
    "title": "Coach session scheduled", "body": "Your coach scheduled a new session.",
    "is_read": False, "created_at": "2024-06-01T09:00:00", "updated_at": "2024-06-01T09:00:00",
}

FAKE_NOTIFICATION = {
    "id": 1, "userId": 2, "type": "coach_session", "mode": "client",
    "conversationId": None, "referenceId": 1,
    "metadata": {"route": "/client/workouts", "event_id": 1},
    "title": "Coach session scheduled", "body": "Your coach scheduled a new session.",
    "isRead": False, "createdAt": "2024-06-01T09:00:00", "updatedAt": "2024-06-01T09:00:00",
}


class TestParseMetadata:
    def test_noneReturnsEmpty(self):
        from app.services.notifications.get_Notifications import parse_metadata
        assert parse_metadata(None) == {}

    def test_dictPassthrough(self):
        from app.services.notifications.get_Notifications import parse_metadata
        data = {"key": "value"}
        assert parse_metadata(data) == data

    def test_validJsonString(self):
        from app.services.notifications.get_Notifications import parse_metadata
        result = parse_metadata('{"key": "value"}')
        assert result["key"] == "value"

    def test_invalidJsonStringReturnsEmpty(self):
        from app.services.notifications.get_Notifications import parse_metadata
        assert parse_metadata("not json") == {}


class TestMakeJsonSafe:
    def test_stringPassthrough(self):
        from app.services.notifications.get_Notifications import make_json_safe
        assert make_json_safe("hello") == "hello"

    def test_datetimeToIso(self):
        from app.services.notifications.get_Notifications import make_json_safe
        from datetime import datetime
        dt = datetime(2024, 6, 1, 9, 0, 0)
        assert make_json_safe(dt) == "2024-06-01T09:00:00"

    def test_dateToIso(self):
        from app.services.notifications.get_Notifications import make_json_safe
        from datetime import date
        d = date(2024, 6, 1)
        assert make_json_safe(d) == "2024-06-01"


class TestGetUserNotifications:
    def test_returnsNotifications(self):
        from app.services.notifications.get_Notifications import get_user_notifications
        with patch(f"{SVC}.run_query", return_value=[FAKE_ROW]):
            result = get_user_notifications(user_id=2, mode="client")
        assert len(result) == 1
        assert result[0]["title"] == "Coach session scheduled"
        assert result[0]["isRead"] is False

    def test_returnsEmptyList(self):
        from app.services.notifications.get_Notifications import get_user_notifications
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_user_notifications(user_id=2, mode="client")
        assert result == []

    def test_parsesMetadata(self):
        from app.services.notifications.get_Notifications import get_user_notifications
        with patch(f"{SVC}.run_query", return_value=[FAKE_ROW]):
            result = get_user_notifications(user_id=2, mode="client")
        assert result[0]["metadata"]["event_id"] == 1


class TestGetNotificationsRoute:
    def test_unauthorized(self, client):
        res = client.get("/notifications/getNotifications?mode=client")
        assert res.status_code == 401

    def test_missingMode(self, auth_client):
        res = auth_client.get("/notifications/getNotifications")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_user_notifications", return_value=[FAKE_NOTIFICATION]):
            with patch(f"{ROUTE}.get_unread_count", return_value=1):
                res = auth_client.get("/notifications/getNotifications?mode=client")
        assert res.status_code == 200
        data = res.get_json()
        assert "notifications" in data
        assert data["count"] == 1

    def test_successCoachMode(self, coach_client):
        with patch(f"{ROUTE}.get_user_notifications", return_value=[]):
            with patch(f"{ROUTE}.get_unread_count", return_value=0):
                res = coach_client.get("/notifications/getNotifications?mode=coach")
        assert res.status_code == 200