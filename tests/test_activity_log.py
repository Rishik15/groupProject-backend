"""
tests/test_activity_log.py

Covers:
  - app/services/activityLog/activityLogService.py
  - app/routes/activityLog/activityLogRoutes.py
"""

import pytest
from unittest.mock import patch


PatchTarget = "app.services.activityLog.activityLogService"

class TestToInt:
    def test_valid_int(self):
        from app.services.activityLog.activityLogService import _to_int
        assert _to_int(5) == 5

    def test_valid_string_int(self):
        from app.services.activityLog.activityLogService import _to_int
        assert _to_int("10") == 10

    def test_none_returns_none(self):
        from app.services.activityLog.activityLogService import _to_int
        assert _to_int(None) is None

    def test_empty_string_returns_none(self):
        from app.services.activityLog.activityLogService import _to_int
        assert _to_int("") is None

    def test_invalid_string_returns_none(self):
        from app.services.activityLog.activityLogService import _to_int
        assert _to_int("abc") is None


class TestToFloat:
    def test_valid_float(self):
        from app.services.activityLog.activityLogService import _to_float
        assert _to_float(3.14) == 3.14

    def test_valid_string_float(self):
        from app.services.activityLog.activityLogService import _to_float
        assert _to_float("2.5") == 2.5

    def test_none_returns_none(self):
        from app.services.activityLog.activityLogService import _to_float
        assert _to_float(None) is None

    def test_empty_string_returns_none(self):
        from app.services.activityLog.activityLogService import _to_float
        assert _to_float("") is None

    def test_invalid_string_returns_none(self):
        from app.services.activityLog.activityLogService import _to_float
        assert _to_float("abc") is None


class TestFormatDatetime:
    def test_none_returns_none(self):
        from app.services.activityLog.activityLogService import _format_datetime
        assert _format_datetime(None) is None

    def test_value_returns_string(self):
        from app.services.activityLog.activityLogService import _format_datetime
        assert _format_datetime("2024-01-01 10:00:00") == "2024-01-01 10:00:00"


class TestFormatStrengthLogs:
    def test_formats_correctly(self):
        from app.services.activityLog.activityLogService import _format_strength_logs
        rows = [{
            "set_log_id": 1,
            "session_id": 10,
            "exercise_id": 5,
            "exercise_name": "Bench Press",
            "set_number": 1,
            "reps": 10,
            "weight": 100.0,
            "rpe": 8.0,
            "performed_at": "2024-01-01 10:00:00",
            "started_at": "2024-01-01 09:00:00",
            "ended_at": None,
            "plan_name": "Push Day",
            "day_label": "Day 1",
            "can_edit": 1,
        }]
        result = _format_strength_logs(rows)
        assert len(result) == 1
        assert result[0]["exerciseName"] == "Bench Press"
        assert result[0]["weight"] == 100.0
        assert result[0]["canEdit"] is True

    def test_empty_rows_returns_empty_list(self):
        from app.services.activityLog.activityLogService import _format_strength_logs
        assert _format_strength_logs([]) == []

    def test_null_weight_and_rpe(self):
        from app.services.activityLog.activityLogService import _format_strength_logs
        rows = [{
            "set_log_id": 1, "session_id": 1, "exercise_id": 1,
            "exercise_name": "Squat", "set_number": 1, "reps": 5,
            "weight": None, "rpe": None, "performed_at": None,
            "started_at": None, "ended_at": None,
            "plan_name": None, "day_label": None, "can_edit": 0,
        }]
        result = _format_strength_logs(rows)
        assert result[0]["weight"] is None
        assert result[0]["rpe"] is None


class TestFormatCardioLogs:
    def test_formats_correctly(self):
        from app.services.activityLog.activityLogService import _format_cardio_logs
        rows = [{
            "cardio_log_id": 1, "session_id": 10, "user_id": 2,
            "performed_at": "2024-01-01 10:00:00", "steps": 5000,
            "distance_km": 3.5, "duration_min": 30, "calories": 200, "avg_hr": 140,
            "can_edit": 1,
        }]
        result = _format_cardio_logs(rows)
        assert result[0]["steps"] == 5000
        assert result[0]["distanceKm"] == 3.5
        assert result[0]["canEdit"] is True

    def test_null_distance(self):
        from app.services.activityLog.activityLogService import _format_cardio_logs
        rows = [{
            "cardio_log_id": 1, "session_id": 1, "user_id": 2,
            "performed_at": None, "steps": None,
            "distance_km": None, "duration_min": None, "calories": None, "avg_hr": None,
            "can_edit": 0,
        }]
        result = _format_cardio_logs(rows)
        assert result[0]["distanceKm"] is None

class TestGetActivityLogs:
    def test_returns_logs_no_session_filter(self):
        from app.services.activityLog.activityLogService import get_activity_logs

        strength_row = {
            "set_log_id": 1, "session_id": 10, "exercise_id": 5,
            "exercise_name": "Bench Press", "set_number": 1, "reps": 10,
            "weight": 100.0, "rpe": 8.0, "performed_at": "2024-01-01",
            "started_at": None, "ended_at": None,
            "plan_name": None, "day_label": None, "can_edit": 1,
        }
        cardio_row = {
            "cardio_log_id": 1, "session_id": 10, "user_id": 2,
            "performed_at": "2024-01-01", "steps": 1000,
            "distance_km": 1.0, "duration_min": 10, "calories": 100, "avg_hr": 120,
            "can_edit": 1,
        }

        with patch(f"{PatchTarget}.run_query", side_effect=[strength_row, cardio_row]):
            pass

        with patch(f"{PatchTarget}.run_query", side_effect=[[strength_row], [cardio_row]]):
            result = get_activity_logs(user_id=2)

        assert result["success"] is True
        assert len(result["strengthLogs"]) == 1
        assert len(result["cardioLogs"]) == 1

    def test_session_not_found(self):
        from app.services.activityLog.activityLogService import get_activity_logs

        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = get_activity_logs(user_id=2, session_id=99)

        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_with_valid_session_id(self):
        from app.services.activityLog.activityLogService import get_activity_logs

        session_row = {"session_id": 10, "ended_at": None}

        with patch(f"{PatchTarget}.run_query", side_effect=[[session_row], [], [],]):
            result = get_activity_logs(user_id=2, session_id=10)
            
        assert result["success"] is True
        assert result["sessionId"] == 10


class TestGetFullActivityLogs:
    def test_returns_all_logs(self):
        from app.services.activityLog.activityLogService import get_full_activity_logs

        with patch(f"{PatchTarget}.run_query", side_effect=[[], []]):
            result = get_full_activity_logs(user_id=2)

        assert result["success"] is True
        assert result["strengthLogs"] == []
        assert result["cardioLogs"] == []

    def test_returns_strength_and_cardio(self):
        from app.services.activityLog.activityLogService import get_full_activity_logs

        strength_row = {
            "set_log_id": 1, "session_id": 1, "exercise_id": 1,
            "exercise_name": "Squat", "set_number": 1, "reps": 5,
            "weight": 120.0, "rpe": 9.0, "performed_at": "2024-01-01",
            "started_at": None, "ended_at": None,
            "plan_name": "Leg Day", "day_label": "Day 2", "can_edit": 0,
        }

        with patch(f"{PatchTarget}.run_query", side_effect=[[strength_row], []]):
            result = get_full_activity_logs(user_id=2)

        assert len(result["strengthLogs"]) == 1
        assert result["strengthLogs"][0]["canEdit"] is False  


class TestLogStrengthSet:
    def test_missing_session_id(self):
        from app.services.activityLog.activityLogService import log_strength_set
        result = log_strength_set(user_id=2, data={"exercise_id": 1, "set_number": 1})
        assert result["success"] is False
        assert result["reason"] == "missing_session"

    def test_missing_exercise_id(self):
        from app.services.activityLog.activityLogService import log_strength_set
        result = log_strength_set(user_id=2, data={"session_id": 10, "set_number": 1})
        assert result["success"] is False
        assert result["reason"] == "missing_exercise"

    def test_missing_set_number(self):
        from app.services.activityLog.activityLogService import log_strength_set
        result = log_strength_set(user_id=2, data={"session_id": 10, "exercise_id": 1})
        assert result["success"] is False
        assert result["reason"] == "missing_set_number"

    def test_session_not_found(self):
        from app.services.activityLog.activityLogService import log_strength_set
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = log_strength_set(user_id=2, data={
                "session_id": 99, "exercise_id": 1, "set_number": 1
            })
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_session_already_finished(self):
        from app.services.activityLog.activityLogService import log_strength_set
        finished_session = [{"session_id": 10, "ended_at": "2024-01-01 11:00:00"}]
        with patch(f"{PatchTarget}.run_query", return_value=finished_session):
            result = log_strength_set(user_id=2, data={
                "session_id": 10, "exercise_id": 1, "set_number": 1
            })
        assert result["success"] is False
        assert result["reason"] == "session_finished"

    def test_exercise_not_found(self):
        from app.services.activityLog.activityLogService import log_strength_set
        active_session = [{"session_id": 10, "ended_at": None}]
        with patch(f"{PatchTarget}.run_query", side_effect=[active_session, [],] ):
            result = log_strength_set(user_id=2, data={"session_id": 10, "exercise_id": 999, "set_number": 1})
        assert result["success"] is False
        assert result["reason"] == "exercise_not_found"

    def test_success(self):
        from app.services.activityLog.activityLogService import log_strength_set
        active_session = [{"session_id": 10, "ended_at": None}]
        exercise_row = [{"exercise_id": 1}]
        with patch(f"{PatchTarget}.run_query", side_effect=[ active_session, exercise_row, 42,]):
            result = log_strength_set(user_id=2, data={
                "session_id": 10, "exercise_id": 1,
                "set_number": 1, "reps": 10, "weight": 100, "rpe": 8
            })
        assert result["success"] is True
        assert result["setLogId"] == 42


class TestUpdateStrengthSet:
    def test_missing_set_number(self):
        from app.services.activityLog.activityLogService import update_strength_set
        result = update_strength_set(user_id=2, set_log_id=1, data={"reps": 10})
        assert result["success"] is False
        assert result["reason"] == "missing_set_number"

    def test_log_not_found(self):
        from app.services.activityLog.activityLogService import update_strength_set
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = update_strength_set(user_id=2, set_log_id=99, data={"set_number": 1})
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_not_todays_log(self):
        from app.services.activityLog.activityLogService import update_strength_set
        existing = [{"set_log_id": 1}]
        with patch(f"{PatchTarget}.run_query", side_effect=[existing, 0]):
            result = update_strength_set(user_id=2, set_log_id=1, data={"set_number": 1})
        assert result["success"] is False
        assert result["reason"] == "not_editable"

    def test_success(self):
        from app.services.activityLog.activityLogService import update_strength_set
        existing = [{"set_log_id": 1}]
        with patch(f"{PatchTarget}.run_query", side_effect=[existing, 1]):
            result = update_strength_set(user_id=2, set_log_id=1, data={"set_number": 2, "reps": 8, "weight": 110, "rpe": 9})
        assert result["success"] is True
        assert result["setLogId"] == 1


class TestLogCardioActivity:
    def test_empty_log(self):
        from app.services.activityLog.activityLogService import log_cardio_activity
        result = log_cardio_activity(user_id=2, data={})
        assert result["success"] is False
        assert result["reason"] == "empty_log"

    def test_session_not_found(self):
        from app.services.activityLog.activityLogService import log_cardio_activity
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = log_cardio_activity(user_id=2, data={
                "session_id": 99, "steps": 1000
            })
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_session_already_finished(self):
        from app.services.activityLog.activityLogService import log_cardio_activity
        finished = [{"session_id": 10, "ended_at": "2024-01-01 11:00:00"}]
        with patch(f"{PatchTarget}.run_query", return_value=finished):
            result = log_cardio_activity(user_id=2, data={
                "session_id": 10, "steps": 1000
            })
        assert result["success"] is False
        assert result["reason"] == "session_finished"

    def test_success_no_session(self):
        from app.services.activityLog.activityLogService import log_cardio_activity
        with patch(f"{PatchTarget}.run_query", return_value=7):
            result = log_cardio_activity(user_id=2, data={"steps": 5000})
        assert result["success"] is True
        assert result["cardioLogId"] == 7

    def test_success_with_session(self):
        from app.services.activityLog.activityLogService import log_cardio_activity
        active_session = [{"session_id": 10, "ended_at": None}]
        with patch(f"{PatchTarget}.run_query", side_effect=[active_session, 8]):
            result = log_cardio_activity(user_id=2, data={
                "session_id": 10, "steps": 3000, "duration_min": 20
            })
        assert result["success"] is True
        assert result["cardioLogId"] == 8


class TestUpdateCardioLog:
    def test_empty_log(self):
        from app.services.activityLog.activityLogService import update_cardio_log
        result = update_cardio_log(user_id=2, cardio_log_id=1, data={})
        assert result["success"] is False
        assert result["reason"] == "empty_log"

    def test_not_found(self):
        from app.services.activityLog.activityLogService import update_cardio_log
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = update_cardio_log(user_id=2, cardio_log_id=99, data={"steps": 1000})
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_not_todays_log(self):
        from app.services.activityLog.activityLogService import update_cardio_log
        existing = [{"cardio_log_id": 1}]
        with patch(f"{PatchTarget}.run_query", side_effect=[existing, 0]):
            result = update_cardio_log(user_id=2, cardio_log_id=1, data={"steps": 1000})
        assert result["success"] is False
        assert result["reason"] == "not_editable"

    def test_success(self):
        from app.services.activityLog.activityLogService import update_cardio_log
        existing = [{"cardio_log_id": 1}]
        with patch(f"{PatchTarget}.run_query", side_effect=[existing, 1]):
            result = update_cardio_log(user_id=2, cardio_log_id=1, data={"steps": 6000, "distance_km": 4.0})
        assert result["success"] is True
        assert result["cardioLogId"] == 1



ROUTE_PatchTarget = "app.routes.activityLog.activityLogRoutes"


class TestGetActivityLogsRoute:
    def test_unauthorized(self, client):
        res = client.get("/activity-log/logs")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.get_activity_logs", return_value={
            "success": True, "sessionId": None,
            "strengthLogs": [], "cardioLogs": []
        }):
            res = auth_client.get("/activity-log/logs")
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_with_session_id_param(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.get_activity_logs", return_value={
            "success": True, "sessionId": 10,
            "strengthLogs": [], "cardioLogs": []
        }) as mock:
            res = auth_client.get("/activity-log/logs?session_id=10")
        assert res.status_code == 200

    def test_service_failure_returns_400(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.get_activity_logs", return_value={
            "success": False, "reason": "not_found", "message": "Session was not found."
        }):
            res = auth_client.get("/activity-log/logs?session_id=99")
        assert res.status_code == 400


class TestGetFullActivityLogsRoute:
    def test_unauthorized(self, client):
        res = client.get("/activity-log/full-logs")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.get_full_activity_logs", return_value={
            "success": True, "strengthLogs": [], "cardioLogs": []
        }):
            res = auth_client.get("/activity-log/full-logs")
        assert res.status_code == 200


class TestLogStrengthSetRoute:
    def test_unauthorized(self, client):
        res = client.post("/activity-log/strength", json={})
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.log_strength_set", return_value={
            "success": True, "message": "Strength set logged.", "setLogId": 1
        }):
            res = auth_client.post("/activity-log/strength", json={
                "session_id": 10, "exercise_id": 1, "set_number": 1
            })
        assert res.status_code == 200

    def test_failure_returns_400(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.log_strength_set", return_value={
            "success": False, "reason": "missing_session",
            "message": "Start a workout session before logging exercises."
        }):
            res = auth_client.post("/activity-log/strength", json={})
        assert res.status_code == 400


class TestUpdateStrengthSetRoute:
    def test_unauthorized(self, client):
        res = client.patch("/activity-log/strength?set_log_id=1", json={})
        assert res.status_code == 401

    def test_missing_set_log_id(self, auth_client):
        res = auth_client.patch("/activity-log/strength", json={"set_number": 1})
        assert res.status_code == 400
        assert res.get_json()["error"] == "set_log_id is required"

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.update_strength_set", return_value={
            "success": True, "message": "Strength log updated.", "setLogId": 1
        }):
            res = auth_client.patch("/activity-log/strength?set_log_id=1", json={
                "set_number": 2, "reps": 8
            })
        assert res.status_code == 200


class TestLogCardioActivityRoute:
    def test_unauthorized(self, client):
        res = client.post("/activity-log/cardio", json={})
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.log_cardio_activity", return_value={
            "success": True, "message": "Cardio activity logged.", "cardioLogId": 5
        }):
            res = auth_client.post("/activity-log/cardio", json={"steps": 5000})
        assert res.status_code == 200

    def test_failure_returns_400(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.log_cardio_activity", return_value={
            "success": False, "reason": "empty_log",
            "message": "Enter at least one cardio value."
        }):
            res = auth_client.post("/activity-log/cardio", json={})
        assert res.status_code == 400


class TestUpdateCardioLogRoute:
    def test_unauthorized(self, client):
        res = client.patch("/activity-log/cardio?cardio_log_id=1", json={})
        assert res.status_code == 401

    def test_missing_cardio_log_id(self, auth_client):
        res = auth_client.patch("/activity-log/cardio", json={"steps": 1000})
        assert res.status_code == 400
        assert res.get_json()["error"] == "cardio_log_id is required"

    def test_success(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.update_cardio_log", return_value={
            "success": True, "message": "Cardio log updated.", "cardioLogId": 1
        }):
            res = auth_client.patch("/activity-log/cardio?cardio_log_id=1", json={
                "steps": 6000
            })
        assert res.status_code == 200

    def test_failure_returns_400(self, auth_client):
        with patch(f"{ROUTE_PatchTarget}.update_cardio_log", return_value={
            "success": False, "reason": "not_editable",
            "message": "Only today's logs can be edited."
        }):
            res = auth_client.patch("/activity-log/cardio?cardio_log_id=1", json={
                "steps": 1000
            })
        assert res.status_code == 400