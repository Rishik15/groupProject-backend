import json
import pytest
from unittest.mock import patch
from datetime import date, time, datetime

FUNCS = "app.services.workouts.workoutActionsFuncs"
SCHED = "app.services.workouts.workoutSchedule"
ROUTE = "app.routes.workouts.workoutActions"

FAKE_SESSION = {
    "session_id": 10,
    "user_id": 2,
    "started_at": "2024-06-01 09:00:00",
    "ended_at": None,
    "workout_plan_id": 5,
    "notes": None,
}

FAKE_SCHEDULE_EVENT = {
    "event_id": 1,
    "title": "Morning Workout",
    "event_date": "2024-06-01",
    "start_time": "09:00:00",
    "end_time": "10:00:00",
    "session_type": "strength",
    "status": "scheduled",
    "notes": "",
    "workout_plan_id": 5,
    "session_id": None,
}

FAKE_ROW = {
    "event_id": 1,
    "user_id": 2,
    "event_date": date(2024, 6, 1),
    "start_time": time(9, 0),
    "end_time": time(10, 0),
    "event_type": "workout",
    "description": json.dumps({
        "title": "Morning Workout",
        "session_type": "strength",
        "status": "scheduled",
        "notes": "",
        "session_id": None,
    }),
    "workout_plan_id": 5,
}


class TestGetExerciseInfo:
    def test_returnsExercises(self):
        from app.services.workouts.workoutActionsFuncs import get_ExerciseInfo
        row = {"exercise_id": 1, "exercise_name": "Bench Press",
               "order_in_workout": 1, "sets_goal": 3, "reps_goal": 10,
               "weight_goal": 100.0, "equipment": "Barbell",
               "video_url": None, "day_order": 1, "day_label": "Day 1"}
        with patch(f"{FUNCS}.run_query", return_value=[row]):
            result = get_ExerciseInfo(plan_id=5)
        assert len(result) == 1
        assert result[0]["exercise_name"] == "Bench Press"

    def test_returnsEmptyList(self):
        from app.services.workouts.workoutActionsFuncs import get_ExerciseInfo
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = get_ExerciseInfo(plan_id=999)
        assert result == []


class TestGetPlanNamesAndIds:
    def test_returnsPlans(self):
        from app.services.workouts.workoutActionsFuncs import getPlanNamesAndIds
        row = {"session_id": 10, "workout_plan_id": 5, "plan_name": "Push Day"}
        with patch(f"{FUNCS}.run_query", return_value=[row]):
            result = getPlanNamesAndIds(user_id=2)
        assert len(result) == 1
        assert result[0]["plan_name"] == "Push Day"

    def test_returnsEmptyList(self):
        from app.services.workouts.workoutActionsFuncs import getPlanNamesAndIds
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = getPlanNamesAndIds(user_id=2)
        assert result == []


class TestStartWorkoutSession:
    def test_returnsCreatedSession(self):
        from app.services.workouts.workoutActionsFuncs import startWorkoutSession
        with patch(f"{FUNCS}.run_query", side_effect=[None, [FAKE_SESSION]]):
            result = startWorkoutSession(user_id=2, workout_plan_id=5)
        assert result["session_id"] == 10

    def test_returnsNoneWhenNoRows(self):
        from app.services.workouts.workoutActionsFuncs import startWorkoutSession
        with patch(f"{FUNCS}.run_query", side_effect=[None, []]):
            result = startWorkoutSession(user_id=2)
        assert result is None


class TestGetWorkoutSessionById:
    def test_returnsSession(self):
        from app.services.workouts.workoutActionsFuncs import getWorkoutSessionById
        with patch(f"{FUNCS}.run_query", return_value=[FAKE_SESSION]):
            result = getWorkoutSessionById(user_id=2, session_id=10)
        assert result["session_id"] == 10

    def test_returnsNoneWhenNotFound(self):
        from app.services.workouts.workoutActionsFuncs import getWorkoutSessionById
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = getWorkoutSessionById(user_id=2, session_id=999)
        assert result is None


class TestGetActiveWorkoutSession:
    def test_returnsActiveSession(self):
        from app.services.workouts.workoutActionsFuncs import getActiveWorkoutSession
        with patch(f"{FUNCS}.run_query", return_value=[FAKE_SESSION]):
            result = getActiveWorkoutSession(user_id=2)
        assert result["session_id"] == 10

    def test_returnsNoneWhenNoActive(self):
        from app.services.workouts.workoutActionsFuncs import getActiveWorkoutSession
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = getActiveWorkoutSession(user_id=2)
        assert result is None


class TestSessionBelongsToUser:
    def test_returnsTrueWhenFound(self):
        from app.services.workouts.workoutActionsFuncs import sessionBelongsToUser
        with patch(f"{FUNCS}.run_query", return_value=[{"session_id": 10}]):
            assert sessionBelongsToUser(2, 10) is True

    def test_returnsFalseWhenNotFound(self):
        from app.services.workouts.workoutActionsFuncs import sessionBelongsToUser
        with patch(f"{FUNCS}.run_query", return_value=[]):
            assert sessionBelongsToUser(2, 999) is False


class TestSessionIsOpen:
    def test_returnsTrueWhenOpen(self):
        from app.services.workouts.workoutActionsFuncs import sessionIsOpen
        with patch(f"{FUNCS}.run_query", return_value=[{"session_id": 10}]):
            assert sessionIsOpen(2, 10) is True

    def test_returnsFalseWhenClosed(self):
        from app.services.workouts.workoutActionsFuncs import sessionIsOpen
        with patch(f"{FUNCS}.run_query", return_value=[]):
            assert sessionIsOpen(2, 10) is False


class TestEndWorkoutSession:
    def test_sessionNotFound(self):
        from app.services.workouts.workoutActionsFuncs import endWorkoutSession
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = endWorkoutSession(user_id=2, session_id=999)
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_sessionAlreadyEnded(self):
        from app.services.workouts.workoutActionsFuncs import endWorkoutSession
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [],
        ]):
            result = endWorkoutSession(user_id=2, session_id=10)
        assert result["success"] is False
        assert result["reason"] == "already_ended"

    def test_success(self):
        from app.services.workouts.workoutActionsFuncs import endWorkoutSession
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [{"session_id": 10}],
            None,
        ]):
            result = endWorkoutSession(user_id=2, session_id=10)
        assert result["success"] is True


class TestGetSessionSets:
    def test_sessionNotFound(self):
        from app.services.workouts.workoutActionsFuncs import getSessionSets
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = getSessionSets(user_id=2, session_id=999)
        assert result["success"] is False

    def test_returnsSets(self):
        from app.services.workouts.workoutActionsFuncs import getSessionSets
        set_row = {"set_log_id": 1, "session_id": 10, "exercise_id": 1,
                   "set_number": 1, "reps": 10, "weight": 100.0,
                   "rpe": 8.0, "performed_at": "2024-06-01 09:30:00"}
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [set_row],
        ]):
            result = getSessionSets(user_id=2, session_id=10)
        assert len(result) == 1


class TestGetSessionCardio:
    def test_sessionNotFound(self):
        from app.services.workouts.workoutActionsFuncs import getSessionCardio
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = getSessionCardio(user_id=2, session_id=999)
        assert result["success"] is False

    def test_returnsCardio(self):
        from app.services.workouts.workoutActionsFuncs import getSessionCardio
        cardio_row = {"cardio_log_id": 1, "session_id": 10, "user_id": 2,
                      "performed_at": "2024-06-01", "steps": 5000,
                      "distance_km": 3.5, "duration_min": 30,
                      "calories": 200, "avg_hr": 140}
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [cardio_row],
        ]):
            result = getSessionCardio(user_id=2, session_id=10)
        assert len(result) == 1


class TestNormalizeSessionType:
    def test_validType(self):
        from app.services.workouts.workoutSchedule import _normalize_session_type
        assert _normalize_session_type("cardio") == "cardio"

    def test_invalidDefaultsToStrength(self):
        from app.services.workouts.workoutSchedule import _normalize_session_type
        assert _normalize_session_type("invalid") == "strength"

    def test_noneDefaultsToStrength(self):
        from app.services.workouts.workoutSchedule import _normalize_session_type
        assert _normalize_session_type(None) == "strength"


class TestNormalizeStatus:
    def test_validStatus(self):
        from app.services.workouts.workoutSchedule import _normalize_status
        assert _normalize_status("done") == "done"

    def test_completeMapsToDown(self):
        from app.services.workouts.workoutSchedule import _normalize_status
        assert _normalize_status("complete") == "done"

    def test_invalidDefaultsToScheduled(self):
        from app.services.workouts.workoutSchedule import _normalize_status
        assert _normalize_status("invalid") == "scheduled"


class TestParseMetadata:
    def test_validJson(self):
        from app.services.workouts.workoutSchedule import _parse_metadata
        data = json.dumps({"title": "Push Day", "session_type": "strength"})
        result = _parse_metadata(data)
        assert result["title"] == "Push Day"

    def test_plainStringReturnsNotes(self):
        from app.services.workouts.workoutSchedule import _parse_metadata
        result = _parse_metadata("some notes")
        assert result["notes"] == "some notes"

    def test_noneReturnsEmpty(self):
        from app.services.workouts.workoutSchedule import _parse_metadata
        assert _parse_metadata(None) == {}


class TestSerializeEventRow:
    def test_serializesCorrectly(self):
        from app.services.workouts.workoutSchedule import _serialize_event_row
        result = _serialize_event_row(FAKE_ROW)
        assert result["event_id"] == 1
        assert result["title"] == "Morning Workout"
        assert result["session_type"] == "strength"

    def test_emptyDescriptionUsesDefaultTitle(self):
        from app.services.workouts.workoutSchedule import _serialize_event_row
        row = {**FAKE_ROW, "description": None}
        result = _serialize_event_row(row)
        assert result["title"] == "Workout Session"


class TestGetWorkoutScheduleEventsForRange:
    def test_returnsEvents(self):
        from app.services.workouts.workoutSchedule import getWorkoutScheduleEventsForRange
        with patch(f"{SCHED}.run_query", return_value=[FAKE_ROW]):
            result = getWorkoutScheduleEventsForRange(2, date(2024, 6, 1), date(2024, 6, 7))
        assert len(result) == 1
        assert result[0]["title"] == "Morning Workout"

    def test_returnsEmptyList(self):
        from app.services.workouts.workoutSchedule import getWorkoutScheduleEventsForRange
        with patch(f"{SCHED}.run_query", return_value=[]):
            result = getWorkoutScheduleEventsForRange(2, date(2024, 6, 1), date(2024, 6, 7))
        assert result == []


class TestDeleteWorkoutScheduleEvent:
    def test_returnsFalseWhenNotFound(self):
        from app.services.workouts.workoutSchedule import deleteWorkoutScheduleEvent
        with patch(f"{SCHED}.run_query", return_value=[]):
            result = deleteWorkoutScheduleEvent(user_id=2, event_id=999)
        assert result is False

    def test_returnsTrueOnSuccess(self):
        from app.services.workouts.workoutSchedule import deleteWorkoutScheduleEvent
        with patch(f"{SCHED}.run_query", side_effect=[[FAKE_ROW], None]):
            result = deleteWorkoutScheduleEvent(user_id=2, event_id=1)
        assert result is True


class TestGetPlanIdSessionIdRoute:
    def test_unauthorized(self, client):
        res = client.get("/workoutAction/getSWPids")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.getPlanNamesAndIds",
                   return_value=[{"session_id": 10, "workout_plan_id": 5, "plan_name": "Push Day"}]):
            res = auth_client.get("/workoutAction/getSWPids")
        assert res.status_code == 200
        assert res.get_json()["message"] == "successful"


class TestGetExerciseInfoRoute:
    def test_unauthorized(self, client):
        res = client.get("/workoutAction/getExerciseInfo", json={"workout_plan_id": 5})
        assert res.status_code == 401

    def test_missingPlanId(self, auth_client):
        res = auth_client.get("/workoutAction/getExerciseInfo", json={})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.get_ExerciseInfo", return_value=[]):
            res = auth_client.get("/workoutAction/getExerciseInfo", json={"workout_plan_id": 5})
        assert res.status_code == 200


class TestGetActiveWorkoutSessionRoute:
    def test_unauthorized(self, client):
        res = client.get("/workoutAction/active")
        assert res.status_code == 401

    def test_noActiveSession(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.getActiveWorkoutSession", return_value=None):
            res = auth_client.get("/workoutAction/active")
        assert res.status_code == 200
        assert res.get_json()["session"] is None

    def test_activeSessionWithSetsAndCardio(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.getActiveWorkoutSession", return_value=FAKE_SESSION):
            with patch(f"{ROUTE}.workoutActionsFuncs.getSessionSets", return_value=[]):
                with patch(f"{ROUTE}.workoutActionsFuncs.getSessionCardio", return_value=[]):
                    res = auth_client.get("/workoutAction/active")
        assert res.status_code == 200
        assert res.get_json()["session"]["session_id"] == 10


class TestStartWorkoutSessionRoute:
    def test_unauthorized(self, client):
        res = client.post("/workoutAction/start", json={})
        assert res.status_code == 401

    def test_successNoPlan(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.startWorkoutSession", return_value=FAKE_SESSION):
            res = auth_client.post("/workoutAction/start", json={})
        assert res.status_code == 201

    def test_successWithPlan(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.startWorkoutSession", return_value=FAKE_SESSION):
            res = auth_client.post("/workoutAction/start", json={"workout_plan_id": 5})
        assert res.status_code == 201
        assert res.get_json()["session"]["session_id"] == 10


class TestGetWorkoutSessionRoute:
    def test_unauthorized(self, client):
        res = client.get("/workoutAction/get_workout?session_id=10")
        assert res.status_code == 401

    def test_missingSessionId(self, auth_client):
        res = auth_client.get("/workoutAction/get_workout")
        assert res.status_code == 400

    def test_sessionNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.getWorkoutSessionById", return_value=None):
            res = auth_client.get("/workoutAction/get_workout?session_id=999")
        assert res.status_code == 404

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.getWorkoutSessionById", return_value=FAKE_SESSION):
            with patch(f"{ROUTE}.workoutActionsFuncs.getSessionSets", return_value=[]):
                with patch(f"{ROUTE}.workoutActionsFuncs.getSessionCardio", return_value=[]):
                    res = auth_client.get("/workoutAction/get_workout?session_id=10")
        assert res.status_code == 200


class TestMarkDoneRoute:
    def test_unauthorized(self, client):
        res = client.patch("/workoutAction/mark_workout_done", json={"session_id": 10})
        assert res.status_code == 401

    def test_missingSessionId(self, auth_client):
        res = auth_client.patch("/workoutAction/mark_workout_done", json={})
        assert res.status_code == 400

    def test_sessionNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.endWorkoutSession",
                   return_value={"success": False, "reason": "not_found"}):
            res = auth_client.patch("/workoutAction/mark_workout_done", json={"session_id": 999})
        assert res.status_code == 404

    def test_alreadyEnded(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.endWorkoutSession",
                   return_value={"success": False, "reason": "already_ended"}):
            res = auth_client.patch("/workoutAction/mark_workout_done", json={"session_id": 10})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutActionsFuncs.endWorkoutSession",
                   return_value={"success": True}):
            res = auth_client.patch("/workoutAction/mark_workout_done", json={"session_id": 10})
        assert res.status_code == 200


class TestGetWorkoutScheduleRoute:
    def test_unauthorized(self, client):
        res = client.get("/workoutAction/schedule?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 401

    def test_missingDates(self, auth_client):
        res = auth_client.get("/workoutAction/schedule")
        assert res.status_code == 400

    def test_endBeforeStart(self, auth_client):
        res = auth_client.get("/workoutAction/schedule?start_date=2024-06-07&end_date=2024-06-01")
        assert res.status_code == 400

    def test_invalidDateFormat(self, auth_client):
        res = auth_client.get("/workoutAction/schedule?start_date=01-06-2024&end_date=07-06-2024")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutSchedule.getWorkoutScheduleEventsForRange",
                   return_value=[FAKE_SCHEDULE_EVENT]):
            res = auth_client.get("/workoutAction/schedule?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 200
        assert len(res.get_json()["events"]) == 1


class TestCreateWorkoutScheduleEventRoute:
    def test_unauthorized(self, client):
        res = client.post("/workoutAction/schedule", json={})
        assert res.status_code == 401

    def test_missingRequiredFields(self, auth_client):
        res = auth_client.post("/workoutAction/schedule", json={"title": "Push Day"})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutSchedule.createWorkoutScheduleEvent",
                   return_value=FAKE_SCHEDULE_EVENT):
            res = auth_client.post("/workoutAction/schedule", json={
                "title": "Morning Workout",
                "event_date": "2024-06-01",
                "start_time": "09:00",
                "end_time": "10:00",
            })
        assert res.status_code == 201
        assert res.get_json()["event"]["title"] == "Morning Workout"


class TestUpdateWorkoutScheduleEventRoute:
    def test_unauthorized(self, client):
        res = client.patch("/workoutAction/schedule/1", json={})
        assert res.status_code == 401

    def test_eventNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutSchedule.updateWorkoutScheduleEvent", return_value=None):
            res = auth_client.patch("/workoutAction/schedule/999", json={"title": "New Title"})
        assert res.status_code == 404

    def test_success(self, auth_client):
        updated = {**FAKE_SCHEDULE_EVENT, "title": "Updated Workout"}
        with patch(f"{ROUTE}.workoutSchedule.updateWorkoutScheduleEvent", return_value=updated):
            res = auth_client.patch("/workoutAction/schedule/1", json={"title": "Updated Workout"})
        assert res.status_code == 200
        assert res.get_json()["event"]["title"] == "Updated Workout"


class TestDeleteWorkoutScheduleEventRoute:
    def test_unauthorized(self, client):
        res = client.delete("/workoutAction/schedule/1")
        assert res.status_code == 401

    def test_eventNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutSchedule.deleteWorkoutScheduleEvent", return_value=False):
            res = auth_client.delete("/workoutAction/schedule/999")
        assert res.status_code == 404

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutSchedule.deleteWorkoutScheduleEvent", return_value=True):
            res = auth_client.delete("/workoutAction/schedule/1")
        assert res.status_code == 200