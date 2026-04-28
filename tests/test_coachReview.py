from unittest.mock import patch
from datetime import datetime

RATE = "app.services.coach.rateCoaches"
COACH_INFO = "app.services.coach.getCoachInfo"
ROUTE = "app.routes.coach.coachReview"

FAKE_COACH_INFO = {
    "first_name": "Sam",
    "last_name": "Coach",
    "price": 50.0,
    "coach_description": "Experienced coach",
    "profile_picture": None,
    "weight": 80.0,
    "height": 180.0,
}

FAKE_REVIEW_DATA = {
    "coach_avg_rating": 4.5,
    "reviews": [],
    "coach_first_name": "Sam",
    "coach_last_name": "Coach",
}


class TestGetCoachInformation:
    def test_returnsInfo(self):
        from app.services.coach.getCoachInfo import getCoachInformation
        with patch(f"{COACH_INFO}.run_query", return_value=[FAKE_COACH_INFO]):
            result = getCoachInformation(coach_id=3)
        assert result[0]["first_name"] == "Sam"

    def test_returnsEmptyWhenNotFound(self):
        from app.services.coach.getCoachInfo import getCoachInformation
        with patch(f"{COACH_INFO}.run_query", return_value=[]):
            result = getCoachInformation(coach_id=999)
        assert result == []


class TestSerializeReviewRows:
    def test_serializesCorrectly(self):
        from app.services.coach.rateCoaches import _serialize_review_rows
        rows = [{
            "review_id": 1, "rating": 5, "review_text": "Great!",
            "reviewer_first_name": "Alex", "reviewer_last_name": "Smith",
            "created_at": datetime(2024, 6, 1), "updated_at": datetime(2024, 6, 1),
        }]
        result = _serialize_review_rows(rows)
        assert result[0]["rating"] == 5

    def test_noneTimestamps(self):
        from app.services.coach.rateCoaches import _serialize_review_rows
        rows = [{
            "review_id": 1, "rating": 4, "review_text": "Good",
            "reviewer_first_name": "Alex", "reviewer_last_name": "Smith",
            "created_at": None, "updated_at": None,
        }]
        result = _serialize_review_rows(rows)
        assert result[0]["created_at"] is None


class TestGetReviews:
    def test_coachNotFound(self):
        from app.services.coach.rateCoaches import getReviews
        import pytest
        with patch(f"{RATE}.run_query", return_value=[]):
            with pytest.raises(ValueError):
                getReviews(coach_id=999)

    def test_returnsReviews(self):
        from app.services.coach.rateCoaches import getReviews
        coach_row = [{"coach_id": 3, "coach_first_name": "Sam", "coach_last_name": "Coach"}]
        summary_row = [{"coach_avg_rating": 4.5}]
        review_row = [{
            "review_id": 1, "rating": 5, "review_text": "Great!",
            "reviewer_first_name": "Alex", "reviewer_last_name": "Smith",
            "created_at": datetime(2024, 6, 1), "updated_at": datetime(2024, 6, 1),
        }]
        with patch(f"{RATE}.run_query", side_effect=[coach_row, summary_row, review_row]):
            result = getReviews(coach_id=3)
        assert result["coach_avg_rating"] == 4.5
        assert len(result["reviews"]) == 1

    def test_noRatingsReturnsNone(self):
        from app.services.coach.rateCoaches import getReviews
        coach_row = [{"coach_id": 3, "coach_first_name": "Sam", "coach_last_name": "Coach"}]
        with patch(f"{RATE}.run_query", side_effect=[coach_row, [{"coach_avg_rating": None}], []]):
            result = getReviews(coach_id=3)
        assert result["coach_avg_rating"] is None


class TestClientKnowsCoach:
    def test_returnsTrueWhenContract(self):
        from app.services.coach.rateCoaches import clientKnowsCoach
        with patch(f"{RATE}.run_query", return_value=[{"contract_id": 1}]):
            assert clientKnowsCoach(2, 3) is True

    def test_returnsFalseWhenNoContract(self):
        from app.services.coach.rateCoaches import clientKnowsCoach
        with patch(f"{RATE}.run_query", return_value=[]):
            assert clientKnowsCoach(2, 3) is False


class TestHasExistingReview:
    def test_returnsTrueWhenExists(self):
        from app.services.coach.rateCoaches import hasExistingReview
        with patch(f"{RATE}.run_query", return_value=[{"review_id": 1}]):
            assert hasExistingReview(2, 3) is True

    def test_returnsFalseWhenNone(self):
        from app.services.coach.rateCoaches import hasExistingReview
        with patch(f"{RATE}.run_query", return_value=[]):
            assert hasExistingReview(2, 3) is False


class TestPostReview:
    def test_success(self):
        from app.services.coach.rateCoaches import postReview
        with patch(f"{RATE}.run_query", return_value=None):
            postReview(user_id=2, coach_id=3, rating=5, review_text="Great!")


class TestGetCoachInfoRoute:
    def test_unauthorized(self, client):
        res = client.get("/coach/get_coach_info?coach_id=3")
        assert res.status_code == 401

    def test_missingCoachId(self, auth_client):
        res = auth_client.get("/coach/get_coach_info")
        assert res.status_code == 400

    def test_invalidCoachId(self, auth_client):
        res = auth_client.get("/coach/get_coach_info?coach_id=abc")
        assert res.status_code == 400

    def test_coachNotFound(self, auth_client):
        with patch(f"{ROUTE}.getCoachInformation", return_value=[]):
            res = auth_client.get("/coach/get_coach_info?coach_id=999")
        assert res.status_code == 404

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.getCoachInformation", return_value=[FAKE_COACH_INFO]):
            res = auth_client.get("/coach/get_coach_info?coach_id=3")
        assert res.status_code == 200
        assert res.get_json()["first_name"] == "Sam"


class TestGetCoachReviewRoute:
    def test_missingCoachId(self, client):
        res = client.get("/coach/get_review")
        assert res.status_code == 400

    def test_invalidCoachId(self, client):
        res = client.get("/coach/get_review?coach_id=abc")
        assert res.status_code == 400

    def test_successLoggedOut(self, client):
        with patch(f"{ROUTE}.getReviews", return_value=dict(FAKE_REVIEW_DATA)):
            res = client.get("/coach/get_review?coach_id=3")
        assert res.status_code == 200
        assert res.get_json()["can_review"] is False

    def test_successClientCanReview(self, auth_client):
        with patch(f"{ROUTE}.getReviews", return_value=dict(FAKE_REVIEW_DATA)):
            with patch(f"{ROUTE}.clientKnowsCoach", return_value=True):
                with patch(f"{ROUTE}.hasExistingReview", return_value=False):
                    res = auth_client.get("/coach/get_review?coach_id=3")
        assert res.status_code == 200
        assert res.get_json()["can_review"] is True

    def test_successClientAlreadyReviewed(self, auth_client):
        with patch(f"{ROUTE}.getReviews", return_value=dict(FAKE_REVIEW_DATA)):
            with patch(f"{ROUTE}.clientKnowsCoach", return_value=True):
                with patch(f"{ROUTE}.hasExistingReview", return_value=True):
                    res = auth_client.get("/coach/get_review?coach_id=3")
        assert res.status_code == 200
        assert res.get_json()["can_review"] is False


class TestLeaveCoachReviewRoute:
    def test_unauthorized(self, client):
        res = client.post("/coach/leave_review", json={"coach_id": 3, "rating": 5})
        assert res.status_code == 401

    def test_missingCoachId(self, auth_client):
        res = auth_client.post("/coach/leave_review", json={"rating": 5})
        assert res.status_code == 400

    def test_invalidCoachId(self, auth_client):
        res = auth_client.post("/coach/leave_review", json={"coach_id": "abc", "rating": 5})
        assert res.status_code == 400

    def test_onlyClientsCanReview(self, coach_client):
        res = coach_client.post("/coach/leave_review", json={"coach_id": 3, "rating": 5})
        assert res.status_code == 403

    def test_clientDoesNotKnowCoach(self, auth_client):
        with patch(f"{ROUTE}.clientKnowsCoach", return_value=False):
            res = auth_client.post("/coach/leave_review", json={"coach_id": 3, "rating": 5})
        assert res.status_code == 403

    def test_alreadyReviewed(self, auth_client):
        with patch(f"{ROUTE}.clientKnowsCoach", return_value=True):
            with patch(f"{ROUTE}.hasExistingReview", return_value=True):
                res = auth_client.post("/coach/leave_review", json={"coach_id": 3, "rating": 5})
        assert res.status_code == 409

    def test_invalidRating(self, auth_client):
        with patch(f"{ROUTE}.clientKnowsCoach", return_value=True):
            with patch(f"{ROUTE}.hasExistingReview", return_value=False):
                res = auth_client.post("/coach/leave_review", json={"coach_id": 3, "rating": 6})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.clientKnowsCoach", return_value=True):
            with patch(f"{ROUTE}.hasExistingReview", return_value=False):
                with patch(f"{ROUTE}.postReview", return_value=None):
                    res = auth_client.post("/coach/leave_review", json={
                        "coach_id": 3, "rating": 5, "review_text": "Great coach!"
                    })
        assert res.status_code == 200