# Route: /nutrition/goals — app/routes/nutrition/getGoalsRoute.py
# Service: app/services/nutrition/setGoals.py

from unittest.mock import patch

SVC = "app.services.nutrition.setGoals"
ROUTE = "app.routes.nutrition.getGoalsRoute"

FAKE_GOALS = {
    "user_id": 2, "calories_target": 2000, "protein_target": 150,
    "carbs_target": 250, "fat_target": 65,
    "created_at": "2024-06-01T00:00:00", "updated_at": "2024-06-01T00:00:00",
}


class TestGetUserNutritionGoals:
    def test_returnsGoals(self):
        from app.services.nutrition.setGoals import get_user_nutrition_goals
        with patch(f"{SVC}.run_query", return_value=[FAKE_GOALS]):
            result = get_user_nutrition_goals(user_id=2)
        assert result["calories_target"] == 2000

    def test_returnsNoneWhenNotFound(self):
        from app.services.nutrition.setGoals import get_user_nutrition_goals
        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_user_nutrition_goals(user_id=2)
        assert result is None


class TestUpsertUserNutritionGoals:
    def test_success(self):
        from app.services.nutrition.setGoals import upsert_user_nutrition_goals
        with patch(f"{SVC}.run_query", side_effect=[None, [FAKE_GOALS]]):
            result = upsert_user_nutrition_goals(
                user_id=2, calories_target=2000, protein_target=150,
                carbs_target=250, fat_target=65,
            )
        assert result["calories_target"] == 2000

    def test_partialUpdate(self):
        from app.services.nutrition.setGoals import upsert_user_nutrition_goals
        partial_goals = {**FAKE_GOALS, "protein_target": 180}
        with patch(f"{SVC}.run_query", side_effect=[None, [partial_goals]]):
            result = upsert_user_nutrition_goals(user_id=2, protein_target=180)
        assert result["protein_target"] == 180


class TestGetGoalsRoute:
    def test_unauthorized(self, client):
        res = client.get("/nutrition/goals")
        assert res.status_code == 401

    def test_successWithGoals(self, auth_client):
        with patch(f"{ROUTE}.get_user_nutrition_goals", return_value=FAKE_GOALS):
            res = auth_client.get("/nutrition/goals")
        assert res.status_code == 200
        assert res.get_json()["goals"]["calories_target"] == 2000

    def test_successNoGoals(self, auth_client):
        with patch(f"{ROUTE}.get_user_nutrition_goals", return_value=None):
            res = auth_client.get("/nutrition/goals")
        assert res.status_code == 200
        assert res.get_json()["goals"] is None


class TestSaveGoalsRoute:
    def test_unauthorized(self, client):
        res = client.post("/nutrition/goals", json={"calories_target": 2000})
        assert res.status_code == 401

    def test_noGoalsProvided(self, auth_client):
        res = auth_client.post("/nutrition/goals", json={})
        assert res.status_code == 400

    def test_allNullValues(self, auth_client):
        res = auth_client.post("/nutrition/goals", json={
            "calories_target": None, "protein_target": None,
            "carbs_target": None, "fat_target": None,
        })
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.upsert_user_nutrition_goals", return_value=FAKE_GOALS):
            res = auth_client.post("/nutrition/goals", json={"calories_target": 2000})
        assert res.status_code == 200
        assert res.get_json()["goals"]["calories_target"] == 2000

    def test_successPartialGoals(self, auth_client):
        with patch(f"{ROUTE}.upsert_user_nutrition_goals", return_value=FAKE_GOALS):
            res = auth_client.post("/nutrition/goals", json={"protein_target": 150})
        assert res.status_code == 200