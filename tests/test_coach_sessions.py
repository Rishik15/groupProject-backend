from unittest.mock import patch, MagicMock
from datetime import date, time

SVC = "app.services.coachsession.coachSessionService"
ROUTE = "app.routes.coachsession.coachSessionRoutes"
GET_CLIENT = f"{ROUTE}.getClientIdFromContract"

FAKE_EVENT = {
    "id": "1",
    "eventId": 1,
    "userId": 2,
    "title": "Coach Session • Alex Smith",
    "date": "2024-06-01",
    "startTime": "09:00:00",
    "endTime": "10:00:00",
    "eventType": "coach_session",
    "description": "Coach Session",
    "notes": "",
    "workoutPlanId": None,
    "workoutPlanName": None,
    "workoutDayId": None,
    "workoutDayLabel": None,
    "workoutDayOrder": None,
    "coachSessionId": 1,
    "contractId": 1,
    "coachId": 3,
    "clientId": 2,
    "status": "scheduled",
    "coachFirstName": "Sam",
    "coachLastName": "Coach",
    "clientFirstName": "Alex",
    "clientLastName": "Smith",
    "clientEmail": "alex@example.com",
}

FAKE_ROW = {
    "event_id": 1,
    "user_id": 2,
    "event_date": date(2024, 6, 1),
    "start_time": time(9, 0),
    "end_time": time(10, 0),
    "event_type": "coach_session",
    "description": "Coach Session",
    "notes": "",
    "workout_plan_id": None,
    "workout_day_id": None,
    "workout_plan_name": None,
    "workout_day_label": None,
    "workout_day_order": None,
    "coach_session_id": 1,
    "contract_id": 1,
    "coach_id": 3,
    "client_id": 2,
    "status": "scheduled",
    "coach_first_name": "Sam",
    "coach_last_name": "Coach",
    "client_first_name": "Alex",
    "client_last_name": "Smith",
    "client_email": "alex@example.com",
}


class TestSerializeEvent:
    def test_noneReturnsNone(self):
        from app.services.coachsession.coachSessionService import serialize_event
        assert serialize_event(None) is None

    def test_serializesCorrectly(self):
        from app.services.coachsession.coachSessionService import serialize_event
        result = serialize_event(FAKE_ROW)
        assert result["eventId"] == 1
        assert result["status"] == "scheduled"
        assert result["clientFirstName"] == "Alex"

    def test_titleIncludesClientName(self):
        from app.services.coachsession.coachSessionService import serialize_event
        result = serialize_event(FAKE_ROW)
        assert "Alex" in result["title"]

    def test_fallbackTitleWhenNoDescription(self):
        from app.services.coachsession.coachSessionService import serialize_event
        row = {**FAKE_ROW, "description": None, "client_first_name": None, "client_last_name": None}
        result = serialize_event(row)
        assert result["title"] == "Coach Session"


class TestDateToString:
    def test_noneReturnsNone(self):
        from app.services.coachsession.coachSessionService import date_to_string
        assert date_to_string(None) is None

    def test_dateObject(self):
        from app.services.coachsession.coachSessionService import date_to_string
        assert date_to_string(date(2024, 6, 1)) == "2024-06-01"


class TestTimeToString:
    def test_noneReturnsNone(self):
        from app.services.coachsession.coachSessionService import time_to_string
        assert time_to_string(None) is None

    def test_timeObject(self):
        from app.services.coachsession.coachSessionService import time_to_string
        assert time_to_string(time(9, 0, 0)) == "09:00:00"


class TestGetAllCoachSessionEvents:
    def test_returnsEvents(self):
        from app.services.coachsession.coachSessionService import get_all_coach_session_events
        with patch(f"{SVC}.run_query", return_value=[FAKE_ROW]):
            result = get_all_coach_session_events(3, date(2024, 6, 1), date(2024, 6, 7))
        assert len(result) == 1
        assert result[0]["eventId"] == 1

    def test_returnsEmptyList(self):
        from app.services.coachsession.coachSessionService import get_all_coach_session_events
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_all_coach_session_events(3, date(2024, 6, 1), date(2024, 6, 7))
        assert result == []


class TestGetCoachSessionEventById:
    def test_returnsEvent(self):
        from app.services.coachsession.coachSessionService import get_coach_session_event_by_id
        with patch(f"{SVC}.run_query", return_value=[FAKE_ROW]):
            result = get_coach_session_event_by_id(coach_id=3, event_id=1)
        assert result["eventId"] == 1

    def test_returnsNoneWhenNotFound(self):
        from app.services.coachsession.coachSessionService import get_coach_session_event_by_id
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_coach_session_event_by_id(coach_id=3, event_id=999)
        assert result is None


class TestGetTimeConflicts:
    def test_returnsConflicts(self):
        from app.services.coachsession.coachSessionService import get_time_conflicts
        with patch(f"{SVC}.run_query", return_value=[FAKE_ROW]):
            result = get_time_conflicts(3, date(2024, 6, 1), time(9, 0), time(10, 0))
        assert len(result) == 1

    def test_noConflicts(self):
        from app.services.coachsession.coachSessionService import get_time_conflicts
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_time_conflicts(3, date(2024, 6, 1), time(11, 0), time(12, 0))
        assert result == []


class TestGetCoachSessionEventsRoute:
    def test_unauthorized(self, client):
        res = client.get("/coachsession/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 401

    def test_missingDates(self, coach_client):
        res = coach_client.get("/coachsession/events")
        assert res.status_code == 400

    def test_endBeforeStart(self, coach_client):
        res = coach_client.get("/coachsession/events?start_date=2024-06-07&end_date=2024-06-01")
        assert res.status_code == 400

    def test_invalidDateFormat(self, coach_client):
        res = coach_client.get("/coachsession/events?start_date=bad&end_date=2024-06-07")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_all_coach_session_events", return_value=[FAKE_EVENT]):
            res = coach_client.get("/coachsession/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 200
        assert len(res.get_json()["events"]) == 1


class TestCreateCoachSessionEventRoute:
    def test_unauthorized(self, client):
        res = client.post("/coachsession/events", json={})
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.post("/coachsession/events", json={})
        assert res.status_code == 400

    def test_contractNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.post("/coachsession/events", json={"contract_id": 99})
        assert res.status_code == 403

    def test_missingTimeFields(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/coachsession/events", json={
                "contract_id": 1,
                "event_date": "2024-06-01",
            })
        assert res.status_code == 400

    def test_endTimeBeforeStartTime(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/coachsession/events", json={
                "contract_id": 1,
                "event_date": "2024-06-01",
                "start_time": "10:00",
                "end_time": "09:00",
            })
        assert res.status_code == 400

    def test_timeConflict(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.coachSessionService.get_time_conflicts", return_value=[FAKE_EVENT]):
                res = coach_client.post("/coachsession/events", json={
                    "contract_id": 1,
                    "event_date": "2024-06-01",
                    "start_time": "09:00",
                    "end_time": "10:00",
                })
        assert res.status_code == 409

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.coachSessionService.get_time_conflicts", return_value=[]):
                with patch(f"{ROUTE}.coachSessionService.create_coach_session_event", return_value=FAKE_EVENT):
                    res = coach_client.post("/coachsession/events", json={
                        "contract_id": 1,
                        "event_date": "2024-06-01",
                        "start_time": "09:00",
                        "end_time": "10:00",
                    })
        assert res.status_code == 201


class TestUpdateCoachSessionEventRoute:
    def test_unauthorized(self, client):
        res = client.patch("/coachsession/events?event_id=1", json={})
        assert res.status_code == 401

    def test_missingEventId(self, coach_client):
        res = coach_client.patch("/coachsession/events", json={})
        assert res.status_code == 400

    def test_eventNotFound(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_coach_session_event_by_id", return_value=None):
            res = coach_client.patch("/coachsession/events?event_id=999", json={})
        assert res.status_code == 404

    def test_timeConflict(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_coach_session_event_by_id", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.coachSessionService.get_time_conflicts", return_value=[FAKE_EVENT]):
                res = coach_client.patch("/coachsession/events?event_id=1", json={
                    "event_date": "2024-06-01",
                    "start_time": "09:00",
                    "end_time": "10:00",
                })
        assert res.status_code == 409

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_coach_session_event_by_id", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.coachSessionService.get_time_conflicts", return_value=[]):
                with patch(f"{ROUTE}.coachSessionService.update_coach_session_event", return_value=FAKE_EVENT):
                    res = coach_client.patch("/coachsession/events?event_id=1", json={
                        "description": "Updated Session"
                    })
        assert res.status_code == 200


class TestDeleteCoachSessionEventRoute:
    def test_unauthorized(self, client):
        res = client.delete("/coachsession/events?event_id=1")
        assert res.status_code == 401

    def test_missingEventId(self, coach_client):
        res = coach_client.delete("/coachsession/events")
        assert res.status_code == 400

    def test_eventNotFound(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_coach_session_event_by_id", return_value=None):
            res = coach_client.delete("/coachsession/events?event_id=999")
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.get_coach_session_event_by_id", return_value=FAKE_EVENT):
            with patch(f"{ROUTE}.coachSessionService.delete_coach_session_event", return_value=True):
                res = coach_client.delete("/coachsession/events?event_id=1")
        assert res.status_code == 200


class TestUpdateCoachSessionStatusRoute:
    def test_unauthorized(self, client):
        res = client.patch("/coachsession/status?event_id=1", json={"status": "completed"})
        assert res.status_code == 401

    def test_missingEventId(self, coach_client):
        res = coach_client.patch("/coachsession/status", json={"status": "completed"})
        assert res.status_code == 400

    def test_invalidStatus(self, coach_client):
        res = coach_client.patch("/coachsession/status?event_id=1", json={"status": "invalid"})
        assert res.status_code == 400

    def test_eventNotFound(self, coach_client):
        with patch(f"{ROUTE}.coachSessionService.update_coach_session_status", return_value=None):
            res = coach_client.patch("/coachsession/status?event_id=999", json={"status": "completed"})
        assert res.status_code == 404

    def test_success(self, coach_client):
        updated = {**FAKE_EVENT, "status": "completed"}
        with patch(f"{ROUTE}.coachSessionService.update_coach_session_status", return_value=updated):
            res = coach_client.patch("/coachsession/status?event_id=1", json={"status": "completed"})
        assert res.status_code == 200
        assert res.get_json()["event"]["status"] == "completed"