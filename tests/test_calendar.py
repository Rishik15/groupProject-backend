"""
tests/test_calendar.py

Covers:
  - app/routes/calendar/calendarRoutes.py
  - app/services/calendar/calendarEvents.py
"""

import pytest
from unittest.mock import patch
from datetime import date, time, datetime

PatchTarget = "app.services.calendar.calendarEvents"
ROUTE = "app.routes.calendar.calendarRoutes"

FAKE_EVENT = {
    "id": "1",
    "eventId": 1,
    "userId": 2,
    "title": "Workout Session",
    "date": "2024-06-01",
    "startTime": "09:00:00",
    "endTime": "10:00:00",
    "eventType": "workout",
    "description": "Workout Session",
    "notes": "",
    "workoutPlanId": 5,
    "workoutPlanName": "Push Day",
    "workoutDayId": 3,
    "workoutDayLabel": "Day 1",
    "workoutDayOrder": 1,
}

FAKE_COACH_SESSION_EVENT = {
    **FAKE_EVENT,
    "eventType": "coach_session",
    "title": "Coach Session",
    "workoutPlanId": None,
    "workoutDayId": None,
}


class TestDateToString:
    def test_none_returns_none(self):
        from app.services.calendar.calendarEvents import _date_to_string
        assert _date_to_string(None) is None

    def test_date_object(self):
        from app.services.calendar.calendarEvents import _date_to_string
        assert _date_to_string(date(2024, 6, 1)) == "2024-06-01"

    def test_datetime_object(self):
        from app.services.calendar.calendarEvents import _date_to_string
        assert _date_to_string(datetime(2024, 6, 1, 9, 0)) == "2024-06-01"

    def test_string_passthrough(self):
        from app.services.calendar.calendarEvents import _date_to_string
        assert _date_to_string("2024-06-01") == "2024-06-01"


class TestTimeToString:
    def test_none_returns_none(self):
        from app.services.calendar.calendarEvents import _time_to_string
        assert _time_to_string(None) is None

    def test_time_object(self):
        from app.services.calendar.calendarEvents import _time_to_string
        assert _time_to_string(time(9, 0, 0)) == "09:00:00"

    def test_datetime_object(self):
        from app.services.calendar.calendarEvents import _time_to_string
        assert _time_to_string(datetime(2024, 6, 1, 9, 30)) == "09:30:00"

    def test_string_passthrough(self):
        from app.services.calendar.calendarEvents import _time_to_string
        assert _time_to_string("09:00:00") == "09:00:00"


class TestSerializeEvent:
    def test_none_returns_none(self):
        from app.services.calendar.calendarEvents import _serialize_event
        assert _serialize_event(None) is None

    def test_workout_event(self):
        from app.services.calendar.calendarEvents import _serialize_event
        row = {
            "event_id": 1, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "Push Day",
            "notes": "", "workout_plan_id": 5, "workout_day_id": 3,
            "workout_plan_name": "Push Day", "workout_day_label": "Day 1",
            "workout_day_order": 1,
        }
        result = _serialize_event(row)
        assert result["eventId"] == 1
        assert result["eventType"] == "workout"
        assert result["title"] == "Push Day"

    def test_coach_session_event_title(self):
        from app.services.calendar.calendarEvents import _serialize_event
        row = {
            "event_id": 2, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "coach_session", "description": "",
            "notes": "", "workout_plan_id": None, "workout_day_id": None,
            "workout_plan_name": None, "workout_day_label": None,
            "workout_day_order": None,
        }
        result = _serialize_event(row)
        assert result["title"] == "Coach Session"

    def test_empty_description_falls_back_to_plan_name(self):
        from app.services.calendar.calendarEvents import _serialize_event
        row = {
            "event_id": 3, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "",
            "notes": "", "workout_plan_id": 5, "workout_day_id": None,
            "workout_plan_name": "Leg Day", "workout_day_label": None,
            "workout_day_order": None,
        }
        result = _serialize_event(row)
        assert result["title"] == "Leg Day"



class TestWorkoutPlanExists:
    def test_returns_true_when_found(self):
        from app.services.calendar.calendarEvents import workout_plan_exists
        with patch(f"{PatchTarget}.run_query", return_value=[{"plan_id": 5}]):
            assert workout_plan_exists(5) is True

    def test_returns_false_when_not_found(self):
        from app.services.calendar.calendarEvents import workout_plan_exists
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            assert workout_plan_exists(999) is False


class TestWorkoutDayBelongsToPlan:
    def test_returns_true_when_found(self):
        from app.services.calendar.calendarEvents import workout_day_belongs_to_plan
        with patch(f"{PatchTarget}.run_query", return_value=[{"day_id": 3}]):
            assert workout_day_belongs_to_plan(5, 3) is True

    def test_returns_false_when_not_found(self):
        from app.services.calendar.calendarEvents import workout_day_belongs_to_plan
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            assert workout_day_belongs_to_plan(5, 999) is False


class TestGetEventsForUserRange:
    def test_returns_serialized_events(self):
        from app.services.calendar.calendarEvents import get_events_for_user_range
        row = {
            "event_id": 1, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "Push Day",
            "notes": "", "workout_plan_id": 5, "workout_day_id": 3,
            "workout_plan_name": "Push Day", "workout_day_label": "Day 1",
            "workout_day_order": 1,
        }
        with patch(f"{PatchTarget}.run_query", return_value=[row]):
            result = get_events_for_user_range(2, date(2024, 6, 1), date(2024, 6, 7))
        assert len(result) == 1
        assert result[0]["eventId"] == 1

    def test_returns_empty_list_when_no_events(self):
        from app.services.calendar.calendarEvents import get_events_for_user_range
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = get_events_for_user_range(2, date(2024, 6, 1), date(2024, 6, 7))
        assert result == []


class TestGetEventByIdForUser:
    def test_returns_serialized_event(self):
        from app.services.calendar.calendarEvents import get_event_by_id_for_user
        row = {
            "event_id": 1, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "Push Day",
            "notes": "", "workout_plan_id": 5, "workout_day_id": 3,
            "workout_plan_name": "Push Day", "workout_day_label": "Day 1",
            "workout_day_order": 1,
        }
        with patch(f"{PatchTarget}.run_query", return_value=[row]):
            result = get_event_by_id_for_user(2, 1)
        assert result["eventId"] == 1

    def test_returns_none_when_not_found(self):
        from app.services.calendar.calendarEvents import get_event_by_id_for_user
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = get_event_by_id_for_user(2, 999)
        assert result is None


class TestCreateEvent:
    def test_creates_and_returns_event(self):
        from app.services.calendar.calendarEvents import create_event
        row = {
            "event_id": 1, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "Push Day",
            "notes": "", "workout_plan_id": 5, "workout_day_id": 3,
            "workout_plan_name": "Push Day", "workout_day_label": "Day 1",
            "workout_day_order": 1,
        }
        with patch(f"{PatchTarget}.run_query", side_effect=[1, [row]]):
            result = create_event(
                user_id=2,
                event_date=date(2024, 6, 1),
                start_time=time(9, 0),
                end_time=time(10, 0),
                event_type="workout",
                description="Push Day",
                workout_plan_id=5,
                workout_day_id=3,
            )
        assert result["eventId"] == 1


class TestDeleteEvent:
    def test_returns_false_when_not_found(self):
        from app.services.calendar.calendarEvents import delete_event
        with patch(f"{PatchTarget}.run_query", return_value=[]):
            result = delete_event(2, 999)
        assert result is False

    def test_returns_true_on_success(self):
        from app.services.calendar.calendarEvents import delete_event
        row = {
            "event_id": 1, "user_id": 2, "event_date": date(2024, 6, 1),
            "start_time": time(9, 0), "end_time": time(10, 0),
            "event_type": "workout", "description": "Push",
            "notes": "", "workout_plan_id": 5, "workout_day_id": 3,
            "workout_plan_name": "Push Day", "workout_day_label": "Day 1",
            "workout_day_order": 1,
        }
        with patch(f"{PatchTarget}.run_query", side_effect=[[row], None]):
            result = delete_event(2, 1)
        assert result is True


class TestGetMyCalendarEvents:
    def test_unauthorized(self, client):
        res = client.get("/calendar/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 401

    def test_missing_dates(self, auth_client):
        res = auth_client.get("/calendar/events")
        assert res.status_code == 400

    def test_end_date_before_start_date(self, auth_client):
        res = auth_client.get("/calendar/events?start_date=2024-06-07&end_date=2024-06-01")
        assert res.status_code == 400

    def test_invalid_date_format(self, auth_client):
        res = auth_client.get("/calendar/events?start_date=06-01-2024&end_date=06-07-2024")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_events_for_user_range", return_value=[FAKE_EVENT]):
            res = auth_client.get("/calendar/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 200
        assert res.get_json()["events"] == [FAKE_EVENT]


class TestCreateMyWorkoutEvent:
    def test_unauthorized(self, client):
        res = client.post("/calendar/events", json={})
        assert res.status_code == 401

    def test_missing_required_fields(self, auth_client):
        res = auth_client.post("/calendar/events", json={"event_date": "2024-06-01"})
        assert res.status_code == 400

    def test_missing_workout_plan_id(self, auth_client):
        res = auth_client.post("/calendar/events", json={
            "event_date": "2024-06-01",
            "start_time": "09:00",
            "end_time": "10:00",
        })
        assert res.status_code == 400

    def test_missing_workout_day_id(self, auth_client):
        res = auth_client.post("/calendar/events", json={
            "event_date": "2024-06-01",
            "start_time": "09:00",
            "end_time": "10:00",
            "workout_plan_id": 5,
        })
        assert res.status_code == 400

    def test_end_time_before_start_time(self, auth_client):
        res = auth_client.post("/calendar/events", json={
            "event_date": "2024-06-01",
            "start_time": "10:00",
            "end_time": "09:00",
            "workout_plan_id": 5,
            "workout_day_id": 3,
        })
        assert res.status_code == 400

    def test_workout_plan_not_found(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.workout_plan_exists", return_value=False):
            res = auth_client.post("/calendar/events", json={
                "event_date": "2024-06-01",
                "start_time": "09:00",
                "end_time": "10:00",
                "workout_plan_id": 999,
                "workout_day_id": 3,
            })
        assert res.status_code == 404

    def test_workout_day_not_in_plan(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.workout_plan_exists", return_value=True):
            with patch(f"{ROUTE}.calendarEvents.workout_day_belongs_to_plan", return_value=False):
                res = auth_client.post("/calendar/events", json={
                    "event_date": "2024-06-01",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "workout_plan_id": 5,
                    "workout_day_id": 999,
                })
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.workout_plan_exists", return_value=True):
            with patch(f"{ROUTE}.calendarEvents.workout_day_belongs_to_plan", return_value=True):
                with patch(f"{ROUTE}.calendarEvents.create_event", return_value=FAKE_EVENT):
                    res = auth_client.post("/calendar/events", json={
                        "event_date": "2024-06-01",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "workout_plan_id": 5,
                        "workout_day_id": 3,
                    })
        assert res.status_code == 201
        assert res.get_json()["event"] == FAKE_EVENT


class TestUpdateMyWorkoutEvent:
    def test_unauthorized(self, client):
        res = client.patch("/calendar/events?event_id=1", json={})
        assert res.status_code == 401

    def test_missing_event_id(self, auth_client):
        res = auth_client.patch("/calendar/events", json={})
        assert res.status_code == 400

    def test_event_not_found(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=None):
            res = auth_client.patch("/calendar/events?event_id=999", json={})
        assert res.status_code == 404

    def test_cannot_edit_non_workout_event(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_COACH_SESSION_EVENT):
            res = auth_client.patch("/calendar/events?event_id=1", json={})
        assert res.status_code == 403

    def test_workout_plan_not_found(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.calendarEvents.workout_plan_exists", return_value=False):
                res = auth_client.patch("/calendar/events?event_id=1", json={
                    "workout_plan_id": 999,
                    "workout_day_id": 3,
                })
        assert res.status_code == 404

    def test_success(self, auth_client):
        updated = {**FAKE_EVENT, "description": "Updated"}
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.calendarEvents.workout_plan_exists", return_value=True):
                with patch(f"{ROUTE}.calendarEvents.workout_day_belongs_to_plan", return_value=True):
                    with patch(f"{ROUTE}.calendarEvents.update_event", return_value=updated):
                        res = auth_client.patch("/calendar/events?event_id=1", json={
                            "description": "Updated"
                        })
        assert res.status_code == 200
        assert res.get_json()["event"]["description"] == "Updated"


class TestDeleteMyWorkoutEvent:
    def test_unauthorized(self, client):
        res = client.delete("/calendar/events?event_id=1")
        assert res.status_code == 401

    def test_missing_event_id(self, auth_client):
        res = auth_client.delete("/calendar/events")
        assert res.status_code == 400

    def test_event_not_found(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=None):
            res = auth_client.delete("/calendar/events?event_id=999")
        assert res.status_code == 404

    def test_cannot_delete_non_workout_event(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_COACH_SESSION_EVENT):
            res = auth_client.delete("/calendar/events?event_id=1")
        assert res.status_code == 403

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.calendarEvents.delete_event", return_value=True):
                res = auth_client.delete("/calendar/events?event_id=1")
        assert res.status_code == 200

GET_CLIENT = f"{ROUTE}.getClientIdFromContract"

class TestGetContractCalendarEvents:
    def test_unauthorized(self, client):
        res = client.get("/calendar/contracts/events?contract_id=1&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 401

    def test_missing_contract_id(self, coach_client):
        res = coach_client.get("/calendar/contracts/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 400

    def test_contract_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.get("/calendar/contracts/events?contract_id=99&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 403

    def test_missing_dates(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.get("/calendar/contracts/events?contract_id=1")
        assert res.status_code == 400

    def test_end_date_before_start_date(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.get("/calendar/contracts/events?contract_id=1&start_date=2024-06-07&end_date=2024-06-01")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_events_for_user_range", return_value=[FAKE_EVENT]):
                res = coach_client.get("/calendar/contracts/events?contract_id=1&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 200
        assert res.get_json()["events"] == [FAKE_EVENT]


class TestCreateContractCoachSessionEvent:
    def test_unauthorized(self, client):
        res = client.post("/calendar/contracts/events?contract_id=1", json={})
        assert res.status_code == 401

    def test_missing_contract_id(self, coach_client):
        res = coach_client.post("/calendar/contracts/events", json={})
        assert res.status_code == 400

    def test_contract_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.post("/calendar/contracts/events?contract_id=99", json={})
        assert res.status_code == 403

    def test_missing_time_fields(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/calendar/contracts/events?contract_id=1", json={
                "event_date": "2024-06-01"
            })
        assert res.status_code == 400

    def test_end_time_before_start_time(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/calendar/contracts/events?contract_id=1", json={
                "event_date": "2024-06-01",
                "start_time": "10:00",
                "end_time": "09:00",
            })
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.create_event", return_value=FAKE_COACH_SESSION_EVENT):
                res = coach_client.post("/calendar/contracts/events?contract_id=1", json={
                    "event_date": "2024-06-01",
                    "start_time": "09:00",
                    "end_time": "10:00",
                })
        assert res.status_code == 201


class TestUpdateContractCoachSessionEvent:
    def test_unauthorized(self, client):
        res = client.patch("/calendar/contracts/events?contract_id=1&event_id=1", json={})
        assert res.status_code == 401

    def test_missing_contract_id(self, coach_client):
        res = coach_client.patch("/calendar/contracts/events?event_id=1", json={})
        assert res.status_code == 400

    def test_missing_event_id(self, coach_client):
        res = coach_client.patch("/calendar/contracts/events?contract_id=1", json={})
        assert res.status_code == 400

    def test_contract_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.patch("/calendar/contracts/events?contract_id=99&event_id=1", json={})
        assert res.status_code == 403

    def test_event_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=None):
                res = coach_client.patch("/calendar/contracts/events?contract_id=1&event_id=999", json={})
        assert res.status_code == 404

    def test_cannot_edit_non_coach_session(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_EVENT):
                res = coach_client.patch("/calendar/contracts/events?contract_id=1&event_id=1", json={})
        assert res.status_code == 403

    def test_success(self, coach_client):
        updated = {**FAKE_COACH_SESSION_EVENT, "description": "Updated Session"}
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_COACH_SESSION_EVENT):
                with patch(f"{ROUTE}.calendarEvents.update_event", return_value=updated):
                    res = coach_client.patch("/calendar/contracts/events?contract_id=1&event_id=1", json={
                        "description": "Updated Session"
                    })
        assert res.status_code == 200


class TestDeleteContractCoachSessionEvent:
    def test_unauthorized(self, client):
        res = client.delete("/calendar/contracts/events?contract_id=1&event_id=1")
        assert res.status_code == 401

    def test_missing_contract_id(self, coach_client):
        res = coach_client.delete("/calendar/contracts/events?event_id=1")
        assert res.status_code == 400

    def test_missing_event_id(self, coach_client):
        res = coach_client.delete("/calendar/contracts/events?contract_id=1")
        assert res.status_code == 400

    def test_contract_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.delete("/calendar/contracts/events?contract_id=99&event_id=1")
        assert res.status_code == 403

    def test_event_not_found(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=None):
                res = coach_client.delete("/calendar/contracts/events?contract_id=1&event_id=999")
        assert res.status_code == 404

    def test_cannot_delete_non_coach_session(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_EVENT):
                res = coach_client.delete("/calendar/contracts/events?contract_id=1&event_id=1")
        assert res.status_code == 403

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.calendarEvents.get_event_by_id_for_user", return_value=FAKE_COACH_SESSION_EVENT):
                with patch(f"{ROUTE}.calendarEvents.delete_event", return_value=True):
                    res = coach_client.delete("/calendar/contracts/events?contract_id=1&event_id=1")
        assert res.status_code == 200