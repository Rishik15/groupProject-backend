# Routes: /coach/exercise/my-exercises, /coach/price-updates/my, /client/getPreviousCoaches, /client/reports/my
# Services: app/services/coach/my_Exercises.py, coach_price_updates.py, app/services/client/previous_coaches.py, reports.py

from unittest.mock import patch
from datetime import datetime

MY_EXERCISES_SVC = "app.services.coach.my_Exercises"
PRICE_SVC = "app.services.coach.coach_price_updates"
PREV_COACHES_SVC = "app.services.client.previous_coaches"
REPORTS_SVC = "app.services.client.reports"

MY_EXERCISES_ROUTE = "app.routes.coach.myExercises"
PRICE_ROUTE = "app.routes.coach.price_updates"
PREV_COACHES_ROUTE = "app.routes.client.getPreviousCoaches"
REPORTS_ROUTE = "app.routes.client.reports"

FAKE_EXERCISE = {
    "exercise_id": 1, "exercise_name": "Bench Press",
    "equipment": "Barbell", "description": None,
    "video_url": None, "created_by": 3,
}

FAKE_PRICE_ROW = {
    "request_id": 1, "coach_id": 3, "current_price": 50.0,
    "proposed_price": 75.0, "status": "pending", "admin_action": None,
    "reviewed_by_admin_id": None, "reviewed_at": None,
    "created_at": datetime(2024, 6, 1), "updated_at": datetime(2024, 6, 1),
}

FAKE_COACH_ROW = {
    "coach_id": 3, "full_name": "Sam Coach",
    "email": "sam@example.com", "image": None,
    "contract_status": "active", "last_contract_update": datetime(2024, 6, 1),
}

FAKE_REPORT_ROW = {
    "report_id": 1, "reported_user_id": 3,
    "reported_name": "Sam Coach", "reported_email": "sam@example.com",
    "reason": "Inappropriate behavior", "status": "pending",
    "admin_action": None, "created_at": datetime(2024, 6, 1),
    "updated_at": datetime(2024, 6, 1),
}


class TestGetMyExercises:
    def test_returnsExercises(self):
        from app.services.coach.my_Exercises import get_my_exercises
        with patch(f"{MY_EXERCISES_SVC}.run_query", return_value=[FAKE_EXERCISE]):
            result = get_my_exercises(coach_id=3)
        assert len(result) == 1
        assert result[0]["exercise_name"] == "Bench Press"

    def test_returnsEmptyList(self):
        from app.services.coach.my_Exercises import get_my_exercises
        with patch(f"{MY_EXERCISES_SVC}.run_query", return_value=[]):
            result = get_my_exercises(coach_id=3)
        assert result == []


class TestGetMyPriceUpdates:
    def test_returnsUpdates(self):
        from app.services.coach.coach_price_updates import get_my_price_updates
        with patch(f"{PRICE_SVC}.run_query", return_value=[FAKE_PRICE_ROW]):
            result = get_my_price_updates(coach_id=3)
        assert len(result) == 1
        assert result[0]["proposed_price"] == 75.0

    def test_returnsEmptyList(self):
        from app.services.coach.coach_price_updates import get_my_price_updates
        with patch(f"{PRICE_SVC}.run_query", return_value=[]):
            result = get_my_price_updates(coach_id=3)
        assert result == []

    def test_noneTimestamps(self):
        from app.services.coach.coach_price_updates import get_my_price_updates
        row = {**FAKE_PRICE_ROW, "reviewed_at": None, "created_at": None, "updated_at": None}
        with patch(f"{PRICE_SVC}.run_query", return_value=[row]):
            result = get_my_price_updates(coach_id=3)
        assert result[0]["reviewed_at"] is None
        assert result[0]["created_at"] is None


class TestGetPreviousCoaches:
    def test_returnsCoaches(self):
        from app.services.client.previous_coaches import get_previous_coaches
        with patch(f"{PREV_COACHES_SVC}.run_query", return_value=[FAKE_COACH_ROW]):
            result = get_previous_coaches(user_id=2)
        assert len(result) == 1
        assert result[0]["full_name"] == "Sam Coach"
        assert result[0]["contract_status"] == "active"

    def test_returnsEmptyList(self):
        from app.services.client.previous_coaches import get_previous_coaches
        with patch(f"{PREV_COACHES_SVC}.run_query", return_value=[]):
            result = get_previous_coaches(user_id=2)
        assert result == []


class TestGetMyReports:
    def test_returnsReports(self):
        from app.services.client.reports import get_my_reports
        with patch(f"{REPORTS_SVC}.run_query", return_value=[FAKE_REPORT_ROW]):
            result = get_my_reports(user_id=2)
        assert len(result) == 1
        assert result[0]["reason"] == "Inappropriate behavior"

    def test_returnsEmptyList(self):
        from app.services.client.reports import get_my_reports
        with patch(f"{REPORTS_SVC}.run_query", return_value=[]):
            result = get_my_reports(user_id=2)
        assert result == []

    def test_noneTimestamps(self):
        from app.services.client.reports import get_my_reports
        row = {**FAKE_REPORT_ROW, "created_at": None, "updated_at": None}
        with patch(f"{REPORTS_SVC}.run_query", return_value=[row]):
            result = get_my_reports(user_id=2)
        assert result[0]["created_at"] is None


class TestMyExercisesRoute:
    def test_unauthorized(self, client):
        res = client.get("/coach/exercise/my-exercises?mode=coach")
        assert res.status_code == 401

    def test_wrongMode(self, coach_client):
        res = coach_client.get("/coach/exercise/my-exercises?mode=client")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{MY_EXERCISES_ROUTE}.get_my_exercises", return_value=[FAKE_EXERCISE]):
            res = coach_client.get("/coach/exercise/my-exercises?mode=coach")
        assert res.status_code == 200
        assert len(res.get_json()["exercises"]) == 1


class TestPriceUpdatesRoute:
    def test_unauthorized(self, client):
        res = client.get("/coach/price-updates/my")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{PRICE_ROUTE}.get_my_price_updates", return_value=[]):
            res = coach_client.get("/coach/price-updates/my")
        assert res.status_code == 200
        assert res.get_json()["message"] == "success"


class TestGetPreviousCoachesRoute:
    def test_unauthorized(self, client):
        res = client.get("/client/getPreviousCoaches")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{PREV_COACHES_ROUTE}.get_previous_coaches", return_value=[]):
            res = auth_client.get("/client/getPreviousCoaches")
        assert res.status_code == 200


class TestGetMyReportsRoute:
    def test_unauthorized(self, client):
        res = client.get("/client/reports/my")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{REPORTS_ROUTE}.get_my_reports", return_value=[]):
            res = auth_client.get("/client/reports/my")
        assert res.status_code == 200
        assert res.get_json()["message"] == "success"