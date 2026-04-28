from unittest.mock import patch

SVC = "app.services.workouts.workoutLogging"
FUNCS = "app.services.workouts.workoutActionsFuncs"
ROUTE = "app.routes.workouts.exerciseLogging"


class TestLogWorkoutInformation:
    def test_sessionNotFound(self):
        from app.services.workouts.workoutLogging import logWorkoutInformation
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = logWorkoutInformation(
                user_id=2, session_id=999, exercise_id=1,
                set_number=1, reps=10, weight=100.0, rpe=8.0
            )
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_sessionEnded(self):
        from app.services.workouts.workoutLogging import logWorkoutInformation
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [],
        ]):
            result = logWorkoutInformation(
                user_id=2, session_id=10, exercise_id=1,
                set_number=1, reps=10, weight=100.0, rpe=8.0
            )
        assert result["success"] is False
        assert result["reason"] == "ended"

    def test_success(self):
        from app.services.workouts.workoutLogging import logWorkoutInformation
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [{"session_id": 10}],
        ]):
            with patch(f"{SVC}.run_query", return_value=None):
                result = logWorkoutInformation(
                    user_id=2, session_id=10, exercise_id=1,
                    set_number=1, reps=10, weight=100.0, rpe=8.0
                )
        assert result["success"] is True

    def test_successWithDatetime(self):
        from app.services.workouts.workoutLogging import logWorkoutInformation
        from datetime import datetime
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [{"session_id": 10}],
        ]):
            with patch(f"{SVC}.run_query", return_value=None):
                result = logWorkoutInformation(
                    user_id=2, session_id=10, exercise_id=1,
                    set_number=1, reps=10, weight=100.0, rpe=8.0,
                    datetimeFinished=datetime(2024, 6, 1, 10, 0, 0)
                )
        assert result["success"] is True


class TestLogCardioActivity:
    def test_sessionNotFound(self):
        from app.services.workouts.workoutLogging import logCardioActivity
        with patch(f"{FUNCS}.run_query", return_value=[]):
            result = logCardioActivity(user_id=2, session_id=999, steps=5000)
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_sessionEnded(self):
        from app.services.workouts.workoutLogging import logCardioActivity
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [],
        ]):
            result = logCardioActivity(user_id=2, session_id=10, steps=5000)
        assert result["success"] is False
        assert result["reason"] == "ended"

    def test_successWithSession(self):
        from app.services.workouts.workoutLogging import logCardioActivity
        with patch(f"{FUNCS}.run_query", side_effect=[
            [{"session_id": 10}],
            [{"session_id": 10}],
        ]):
            with patch(f"{SVC}.run_query", return_value=None):
                result = logCardioActivity(user_id=2, session_id=10, steps=5000)
        assert result["success"] is True

    def test_successNoSession(self):
        from app.services.workouts.workoutLogging import logCardioActivity
        with patch(f"{SVC}.run_query", return_value=None):
            result = logCardioActivity(user_id=2, steps=3000, duration_min=30)
        assert result["success"] is True


class TestLogSetsRoute:
    def test_unauthorized(self, client):
        res = client.post("/exerciseLog/log_weights", json={})
        assert res.status_code == 401

    def test_missingRequiredFields(self, auth_client):
        res = auth_client.post("/exerciseLog/log_weights", json={
            "session_id": 10, "exercise_id": 1
        })
        assert res.status_code == 400

    def test_setNumberTooLow(self, auth_client):
        res = auth_client.post("/exerciseLog/log_weights", json={
            "session_id": 10, "exercise_id": 1, "set_number": 0
        })
        assert res.status_code == 400

    def test_negativeReps(self, auth_client):
        res = auth_client.post("/exerciseLog/log_weights", json={
            "session_id": 10, "exercise_id": 1, "set_number": 1, "reps": -1
        })
        assert res.status_code == 400

    def test_negativeWeight(self, auth_client):
        res = auth_client.post("/exerciseLog/log_weights", json={
            "session_id": 10, "exercise_id": 1, "set_number": 1, "weight": -10
        })
        assert res.status_code == 400

    def test_negativeRpe(self, auth_client):
        res = auth_client.post("/exerciseLog/log_weights", json={
            "session_id": 10, "exercise_id": 1, "set_number": 1, "rpe": -1
        })
        assert res.status_code == 400

    def test_sessionNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logWorkoutInformation",
                   return_value={"success": False, "reason": "not_found"}):
            res = auth_client.post("/exerciseLog/log_weights", json={
                "session_id": 999, "exercise_id": 1, "set_number": 1
            })
        assert res.status_code == 404

    def test_sessionEnded(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logWorkoutInformation",
                   return_value={"success": False, "reason": "ended"}):
            res = auth_client.post("/exerciseLog/log_weights", json={
                "session_id": 10, "exercise_id": 1, "set_number": 1
            })
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logWorkoutInformation",
                   return_value={"success": True}):
            res = auth_client.post("/exerciseLog/log_weights", json={
                "session_id": 10, "exercise_id": 1, "set_number": 1,
                "reps": 10, "weight": 100.0, "rpe": 8.0
            })
        assert res.status_code == 200

    def test_successWithDatetime(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logWorkoutInformation",
                   return_value={"success": True}):
            res = auth_client.post("/exerciseLog/log_weights", json={
                "session_id": 10, "exercise_id": 1, "set_number": 1,
                "datetimeFinished": "2024-06-01T10:00:00"
            })
        assert res.status_code == 200


class TestLogCardioRoute:
    def test_unauthorized(self, client):
        res = client.post("/exerciseLog/log_cardio", json={})
        assert res.status_code == 401

    def test_noCardioFields(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={})
        assert res.status_code == 400

    def test_negativeSteps(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={"steps": -100})
        assert res.status_code == 400

    def test_negativeDistanceKm(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={"distance_km": -1.0})
        assert res.status_code == 400

    def test_negativeDurationMin(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={"duration_min": -5})
        assert res.status_code == 400

    def test_negativeCalories(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={"calories": -50})
        assert res.status_code == 400

    def test_negativeAvgHr(self, auth_client):
        res = auth_client.post("/exerciseLog/log_cardio", json={"avg_hr": -10})
        assert res.status_code == 400

    def test_sessionNotFound(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logCardioActivity",
                   return_value={"success": False, "reason": "not_found"}):
            res = auth_client.post("/exerciseLog/log_cardio", json={
                "session_id": 999, "steps": 5000
            })
        assert res.status_code == 404

    def test_sessionEnded(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logCardioActivity",
                   return_value={"success": False, "reason": "ended"}):
            res = auth_client.post("/exerciseLog/log_cardio", json={
                "session_id": 10, "steps": 5000
            })
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logCardioActivity",
                   return_value={"success": True}):
            res = auth_client.post("/exerciseLog/log_cardio", json={"steps": 5000})
        assert res.status_code == 201

    def test_successWithPerformedAt(self, auth_client):
        with patch(f"{ROUTE}.workoutLogging.logCardioActivity",
                   return_value={"success": True}):
            res = auth_client.post("/exerciseLog/log_cardio", json={
                "steps": 5000,
                "performed_at": "2024-06-01T10:00:00"
            })
        assert res.status_code == 201