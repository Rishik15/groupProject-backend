from unittest.mock import patch

SVC = "app.services.sessions.sessionService"
ROUTE = "app.routes.sessions.sessionRoutes"

FAKE_EVENT_ROW = {
    "event_id": 1,
    "user_id": 2,
    "event_date": "2024-06-01",
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "description": "Push Day",
    "notes": None,
    "workout_plan_id": 5,
    "workout_day_id": 3,
    "workout_plan_name": "Push Day",
    "workout_day_label": "Day 1",
    "workout_day_order": 1,
    "session_id": None,
    "started_at": None,
    "ended_at": None,
    "server_time": "09:30:00",
}

FAKE_ACTIVE_SESSION_ROW = {
    "session_id": 10,
    "user_id": 2,
    "event_id": 1,
    "workout_plan_id": 5,
    "workout_day_id": 3,
    "started_at": "2024-06-01 09:00:00",
    "ended_at": None,
    "notes": None,
    "title": "Push Day",
    "workout_plan_name": "Push Day",
    "workout_day_label": "Day 1",
}

FAKE_SESSION_RESULT = {
    "success": True,
    "session": {
        "sessionId": 10,
        "eventId": 1,
        "workoutPlanId": 5,
        "workoutDayId": 3,
        "startedAt": None,
        "endedAt": None,
        "notes": None,
    },
}

FAKE_EXERCISE_ROW = {
    "exercise_id": 1,
    "exercise_name": "Bench Press",
    "equipment": "Barbell",
    "video_url": None,
    "description": None,
    "order_in_workout": 1,
    "sets_goal": 3,
    "reps_goal": 10,
    "weight_goal": 100.0,
}


class TestGetSessionStatus:
    def test_activeWhenNoEndedAt(self):
        from app.services.sessions.sessionService import _get_session_status
        row = {"session_id": 10, "ended_at": None, "end_time": None, "server_time": None}
        assert _get_session_status(row) == "active"

    def test_completedWhenEndedAt(self):
        from app.services.sessions.sessionService import _get_session_status
        row = {"session_id": 10, "ended_at": "2024-06-01 10:00:00", "end_time": None, "server_time": None}
        assert _get_session_status(row) == "completed"

    def test_notStartedWhenNoSession(self):
        from app.services.sessions.sessionService import _get_session_status
        row = {"session_id": None, "ended_at": None, "end_time": None, "server_time": None}
        assert _get_session_status(row) == "not_started"


class TestFormatTime:
    def test_noneReturnsNone(self):
        from app.services.sessions.sessionService import _format_time
        assert _format_time(None) is None

    def test_returnsString(self):
        from app.services.sessions.sessionService import _format_time
        assert _format_time("09:00:00") == "09:00:00"


class TestFormatDatetime:
    def test_noneReturnsNone(self):
        from app.services.sessions.sessionService import _format_datetime
        assert _format_datetime(None) is None

    def test_returnsString(self):
        from app.services.sessions.sessionService import _format_datetime
        assert _format_datetime("2024-06-01 09:00:00") == "2024-06-01 09:00:00"


class TestMapScheduledEvent:
    def test_mapsCorrectly(self):
        from app.services.sessions.sessionService import _map_scheduled_event
        result = _map_scheduled_event(FAKE_EVENT_ROW)
        assert result["eventId"] == 1
        assert result["title"] == "Push Day"
        assert result["sessionStatus"] == "not_started"
        assert result["canStart"] is True

    def test_fallbackTitleWhenNoDescription(self):
        from app.services.sessions.sessionService import _map_scheduled_event
        row = {**FAKE_EVENT_ROW, "description": None}
        result = _map_scheduled_event(row)
        assert result["title"] == "Workout Session"


class TestMapActiveSession:
    def test_noneReturnsNone(self):
        from app.services.sessions.sessionService import _map_active_session
        assert _map_active_session(None) is None

    def test_mapsCorrectly(self):
        from app.services.sessions.sessionService import _map_active_session
        result = _map_active_session(FAKE_ACTIVE_SESSION_ROW)
        assert result["sessionId"] == 10
        assert result["workoutPlanName"] == "Push Day"


class TestGetTodayScheduledSessions:
    def test_returnsEvents(self):
        from app.services.sessions.sessionService import get_today_scheduled_sessions
        with patch(f"{SVC}.run_query", return_value=[FAKE_EVENT_ROW]):
            result = get_today_scheduled_sessions(user_id=2)
        assert result["success"] is True
        assert len(result["events"]) == 1

    def test_returnsEmptyEvents(self):
        from app.services.sessions.sessionService import get_today_scheduled_sessions
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_today_scheduled_sessions(user_id=2)
        assert result["success"] is True
        assert result["events"] == []


class TestGetActiveSession:
    def test_returnsActiveSession(self):
        from app.services.sessions.sessionService import get_active_session
        with patch(f"{SVC}.run_query", return_value=[FAKE_ACTIVE_SESSION_ROW]):
            result = get_active_session(user_id=2)
        assert result["success"] is True
        assert result["session"]["sessionId"] == 10

    def test_returnsNoneWhenNoActive(self):
        from app.services.sessions.sessionService import get_active_session
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_active_session(user_id=2)
        assert result["success"] is True
        assert result["session"] is None


class TestStartScheduledSession:
    def test_eventNotFound(self):
        from app.services.sessions.sessionService import start_scheduled_session
        with patch(f"{SVC}.run_query", return_value=[]):
            result = start_scheduled_session(user_id=2, event_id=999)
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_missingPlanOrDay(self):
        from app.services.sessions.sessionService import start_scheduled_session
        event = {**FAKE_EVENT_ROW, "workout_plan_id": None, "workout_day_id": None}
        with patch(f"{SVC}.run_query", return_value=[event]):
            result = start_scheduled_session(user_id=2, event_id=1)
        assert result["success"] is False
        assert result["reason"] == "invalid_event"

    def test_sessionAlreadyExistsForEvent(self):
        from app.services.sessions.sessionService import start_scheduled_session
        existing_session = {
            "session_id": 10, "event_id": 1, "workout_plan_id": 5,
            "workout_day_id": 3, "started_at": "2024-06-01 09:00:00",
            "ended_at": None, "notes": None,
        }
        with patch(f"{SVC}.run_query", side_effect=[
            [FAKE_EVENT_ROW],
            [existing_session],
        ]):
            result = start_scheduled_session(user_id=2, event_id=1)
        assert result["success"] is True
        assert "already exists" in result["message"]

    def test_openSessionExists(self):
        from app.services.sessions.sessionService import start_scheduled_session
        open_session = {
            "session_id": 10, "event_id": None, "workout_plan_id": 5,
            "workout_day_id": 3, "started_at": "2024-06-01 09:00:00",
            "ended_at": None, "notes": None,
        }
        with patch(f"{SVC}.run_query", side_effect=[
            [FAKE_EVENT_ROW],
            [],
            [open_session],
        ]):
            result = start_scheduled_session(user_id=2, event_id=1)
        assert result["success"] is True
        assert "active session" in result["message"]

    def test_successCreatesNewSession(self):
        from app.services.sessions.sessionService import start_scheduled_session
        with patch(f"{SVC}.run_query", side_effect=[
            [FAKE_EVENT_ROW],
            [],
            [],
            10,
        ]):
            result = start_scheduled_session(user_id=2, event_id=1)
        assert result["success"] is True
        assert result["session"]["sessionId"] == 10


class TestGetSessionExercises:
    def test_sessionNotFound(self):
        from app.services.sessions.sessionService import get_session_exercises
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_session_exercises(user_id=2, session_id=999)
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_missingWorkoutDay(self):
        from app.services.sessions.sessionService import get_session_exercises
        session_row = {"session_id": 10, "workout_day_id": None}
        with patch(f"{SVC}.run_query", return_value=[session_row]):
            result = get_session_exercises(user_id=2, session_id=10)
        assert result["success"] is False
        assert result["reason"] == "missing_workout_day"

    def test_returnsExercises(self):
        from app.services.sessions.sessionService import get_session_exercises
        session_row = {"session_id": 10, "workout_day_id": 3}
        with patch(f"{SVC}.run_query", side_effect=[
            [session_row],
            [FAKE_EXERCISE_ROW],
        ]):
            result = get_session_exercises(user_id=2, session_id=10)
        assert result["success"] is True
        assert len(result["exercises"]) == 1
        assert result["exercises"][0]["exerciseName"] == "Bench Press"

    def test_nullWeightGoal(self):
        from app.services.sessions.sessionService import get_session_exercises
        session_row = {"session_id": 10, "workout_day_id": 3}
        exercise_row = {**FAKE_EXERCISE_ROW, "weight_goal": None}
        with patch(f"{SVC}.run_query", side_effect=[
            [session_row],
            [exercise_row],
        ]):
            result = get_session_exercises(user_id=2, session_id=10)
        assert result["exercises"][0]["weightGoal"] is None


class TestFinishSession:
    def test_sessionNotFound(self):
        from app.services.sessions.sessionService import finish_session
        with patch(f"{SVC}.run_query", return_value=[]):
            result = finish_session(user_id=2, session_id=999)
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_alreadyFinished(self):
        from app.services.sessions.sessionService import finish_session
        session_row = {"session_id": 10, "ended_at": "2024-06-01 10:00:00"}
        with patch(f"{SVC}.run_query", return_value=[session_row]):
            result = finish_session(user_id=2, session_id=10)
        assert result["success"] is True
        assert "already finished" in result["message"]

    def test_success(self):
        from app.services.sessions.sessionService import finish_session
        session_row = {"session_id": 10, "ended_at": None}
        with patch(f"{SVC}.run_query", side_effect=[
            [session_row],
            None,
        ]):
            result = finish_session(user_id=2, session_id=10)
        assert result["success"] is True
        assert result["sessionId"] == 10


class TestScheduledTodayRoute:
    def test_unauthorized(self, client):
        res = client.get("/sessions/scheduled-today")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_today_scheduled_sessions", return_value={
            "success": True, "events": []
        }):
            res = auth_client.get("/sessions/scheduled-today")
        assert res.status_code == 200


class TestActiveSessionRoute:
    def test_unauthorized(self, client):
        res = client.get("/sessions/active")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_active_session", return_value={
            "success": True, "session": None
        }):
            res = auth_client.get("/sessions/active")
        assert res.status_code == 200


class TestStartScheduledSessionRoute:
    def test_unauthorized(self, client):
        res = client.post("/sessions/start-scheduled", json={})
        assert res.status_code == 401

    def test_missingEventId(self, auth_client):
        res = auth_client.post("/sessions/start-scheduled", json={})
        assert res.status_code == 400

    def test_serviceFailure(self, auth_client):
        with patch(f"{ROUTE}.start_scheduled_session", return_value={
            "success": False, "reason": "not_found", "message": "Workout event was not found."
        }):
            res = auth_client.post("/sessions/start-scheduled", json={"event_id": 999})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.start_scheduled_session", return_value=FAKE_SESSION_RESULT):
            res = auth_client.post("/sessions/start-scheduled", json={"event_id": 1})
        assert res.status_code == 200


class TestSessionExercisesRoute:
    def test_unauthorized(self, client):
        res = client.get("/sessions/session-exercises?session_id=10")
        assert res.status_code == 401

    def test_missingSessionId(self, auth_client):
        res = auth_client.get("/sessions/session-exercises")
        assert res.status_code == 400

    def test_serviceFailure(self, auth_client):
        with patch(f"{ROUTE}.get_session_exercises", return_value={
            "success": False, "reason": "not_found", "message": "Session was not found."
        }):
            res = auth_client.get("/sessions/session-exercises?session_id=999")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_session_exercises", return_value={
            "success": True, "sessionId": 10, "workoutDayId": 3, "exercises": []
        }):
            res = auth_client.get("/sessions/session-exercises?session_id=10")
        assert res.status_code == 200


class TestFinishSessionRoute:
    def test_unauthorized(self, client):
        res = client.patch("/sessions/finish", json={})
        assert res.status_code == 401

    def test_missingSessionId(self, auth_client):
        res = auth_client.patch("/sessions/finish", json={})
        assert res.status_code == 400

    def test_serviceFailure(self, auth_client):
        with patch(f"{ROUTE}.finish_session", return_value={
            "success": False, "reason": "not_found", "message": "Session was not found."
        }):
            res = auth_client.patch("/sessions/finish", json={"session_id": 999})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.finish_session", return_value={
            "success": True, "message": "Workout session finished.", "sessionId": 10
        }):
            res = auth_client.patch("/sessions/finish", json={"session_id": 10})
        assert res.status_code == 200