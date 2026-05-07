from unittest.mock import patch
from datetime import datetime

CAL_SVC = "app.services.dashboard.client.getCalories"
WEIGHT_SVC = "app.services.dashboard.client.getWeight"
WORKOUT_SVC = "app.services.dashboard.client.getWorkouts"
NUTRITION_SVC = "app.services.dashboard.client.getDailyNutrition"

CAL_ROUTE = "app.routes.dashboard.client.getCalories"
WEIGHT_ROUTE = "app.routes.dashboard.client.getWeight"
WORKOUT_ROUTE = "app.routes.dashboard.client.getWorkouts"
NUTRITION_ROUTE = "app.routes.dashboard.client.getNutrition"

FAKE_MEAL = {
    "log_id": 1, "user_id": 2, "meal_id": 1, "food_item_id": None,
    "eaten_at": "2024-06-03T08:00:00", "servings": 1,
    "notes": None, "photo_url": None,
    "created_at": "2024-06-03T08:00:00", "updated_at": "2024-06-03T08:00:00",
    "meal_name": "Oatmeal", "calories": 300, "protein": 10.0,
    "carbs": 50.0, "fats": 5.0,
}


class TestGetCaloriesMetricsService:
    def test_returnsSevenDays(self):
        from app.services.dashboard.client.getCalories import get_calories_metrics_service
        with patch(f"{CAL_SVC}.getLoggedMeals", return_value=[]):
            result = get_calories_metrics_service(user_id=2)
        assert len(result) == 7

    def test_calculatesCalories(self):
        from app.services.dashboard.client.getCalories import get_calories_metrics_service
        from datetime import date, timedelta
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        current_meal = {**FAKE_MEAL, "eaten_at": f"{monday}T08:00:00"}
        with patch(f"{CAL_SVC}.getLoggedMeals", return_value=[current_meal]):
            result = get_calories_metrics_service(user_id=2)
        total = sum(day["calories"] for day in result)
        assert total == 300.0

    def test_skipsNullCalories(self):
        from app.services.dashboard.client.getCalories import get_calories_metrics_service
        null_meal = {**FAKE_MEAL, "calories": None}
        with patch(f"{CAL_SVC}.getLoggedMeals", return_value=[null_meal]):
            result = get_calories_metrics_service(user_id=2)
        total = sum(day["calories"] for day in result)
        assert total == 0


class TestGetUserWeight:
    def test_returnsEmptyWhenNoData(self):
        from app.services.dashboard.client.getWeight import get_user_weight
        with patch(f"{WEIGHT_SVC}.run_query", return_value=[]):
            result = get_user_weight(user_id=2)
        assert result == []

    def test_returnsWeeks(self):
        from app.services.dashboard.client.getWeight import get_user_weight
        rows = [
            {"week_number": 1, "avg_weight": 80.0},
            {"week_number": 2, "avg_weight": 79.5},
        ]
        with patch(f"{WEIGHT_SVC}.run_query", return_value=rows):
            result = get_user_weight(user_id=2)
        assert len(result) >= 1
        assert result[0]["avg_weight"] == 80.0

    def test_fillsMissingWeeks(self):
        from app.services.dashboard.client.getWeight import get_user_weight
        rows = [
            {"week_number": 1, "avg_weight": 80.0},
            {"week_number": 3, "avg_weight": 79.0},
        ]
        with patch(f"{WEIGHT_SVC}.run_query", return_value=rows):
            result = get_user_weight(user_id=2)
        assert len(result) == 3
        assert result[1]["avg_weight"] == 80.0


class TestGetWorkoutCompletionService:
    def test_returnsSevenDays(self):
        from app.services.dashboard.client.getWorkouts import get_workout_completion_service
        with patch(f"{WORKOUT_SVC}.run_query", side_effect=[[], []]):
            result = get_workout_completion_service(user_id=2)
        assert len(result["days"]) == 7
        assert result["summary"]["planned"] == 0
        assert result["summary"]["completed"] == 0

    def test_countsPlannedAndCompleted(self):
        from app.services.dashboard.client.getWorkouts import get_workout_completion_service
        from datetime import date, timedelta
        today = date.today()
        start = today - timedelta(days=today.weekday())
        planned_rows = [{"event_date": start, "planned_count": 2}]
        completed_rows = [{"day": start, "completed_count": 1}]
        with patch(f"{WORKOUT_SVC}.run_query", side_effect=[planned_rows, completed_rows]):
            result = get_workout_completion_service(user_id=2)
        assert result["summary"]["planned"] == 2
        assert result["summary"]["completed"] == 1


class TestGetNutrition:
    def test_returnsZerosWithNoMeals(self):
        from app.services.dashboard.client.getDailyNutrition import getNutrition
        with patch(f"{NUTRITION_SVC}.getLoggedMeals", return_value=[]):
            with patch(f"{NUTRITION_SVC}.run_query", return_value=[]):
                result = getNutrition(user_id=2)
        assert result["consumed"]["calories"] == 0
        assert result["target"]["calories"] is None

    def test_calculatesTotals(self):
        from app.services.dashboard.client.getDailyNutrition import getNutrition
        with patch(f"{NUTRITION_SVC}.getLoggedMeals", return_value=[FAKE_MEAL]):
            with patch(f"{NUTRITION_SVC}.run_query", return_value=[{
                "calories_target": 2000, "protein_target": 150,
                "carbs_target": 250, "fat_target": 65,
            }]):
                result = getNutrition(user_id=2)
        assert result["consumed"]["calories"] == 300.0
        assert result["target"]["calories"] == 2000


class TestGetCaloriesRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/client/calories")
        assert res.status_code == 401

    def test_success(self, auth_client):
        fake_weekly = [{"day": "Mon", "calories": 300}]
        with patch(f"{CAL_ROUTE}.get_calories_metrics_service", return_value=fake_weekly):
            res = auth_client.get("/dashboard/client/calories")
        assert res.status_code == 200
        assert "weekly" in res.get_json()


class TestGetWeightRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/client/weight")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{WEIGHT_ROUTE}.get_user_weight", return_value=[]):
            res = auth_client.get("/dashboard/client/weight")
        assert res.status_code == 200
        assert "weekly" in res.get_json()


class TestGetWorkoutCompletionRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/client/workout-completion")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{WORKOUT_ROUTE}.get_workout_completion_service", return_value={
            "days": [], "summary": {"planned": 0, "completed": 0}
        }):
            res = auth_client.get("/dashboard/client/workout-completion")
        assert res.status_code == 200


class TestGetNutritionRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/client/nutrition")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{NUTRITION_ROUTE}.getNutrition", return_value={
            "consumed": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "target": {"calories": None, "protein": None, "carbs": None, "fat": None},
        }):
            res = auth_client.get("/dashboard/client/nutrition")
        assert res.status_code == 200