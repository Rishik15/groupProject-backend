from unittest.mock import patch
from datetime import datetime

GET_MEALS_SVC = "app.services.nutrition.get_Meals"
TODAYS_SVC = "app.services.nutrition.get_Todays_Meals"
WEEKLY_SVC = "app.services.nutrition.get_Weekly_Calories"
NUTRITION_SVC = "app.services.nutrition.get_Nutrition_Today"

GET_MEALS_ROUTE = "app.routes.nutrition.getMeals"
TODAYS_ROUTE = "app.routes.nutrition.getTodaysMeals"
WEEKLY_ROUTE = "app.routes.nutrition.getWeeklyCaloriesSummary"
NUTRITION_ROUTE = "app.routes.nutrition.getNutritionToday"

FAKE_MEAL = {
    "meal_id": 1, "name": "Oatmeal", "calories": 300,
    "protein": 10.0, "carbs": 50.0, "fats": 5.0,
}

FAKE_LOGGED_MEAL = {
    "log_id": 1, "user_id": 2, "meal_id": 1, "food_item_id": None,
    "eaten_at": "2024-06-01T08:00:00", "servings": 1,
    "notes": None, "photo_url": None, "created_at": "2024-06-01T08:00:00",
    "updated_at": "2024-06-01T08:00:00",
    "meal_name": "Oatmeal", "calories": 300, "protein": 10.0,
    "carbs": 50.0, "fats": 5.0,
}



class TestGetMeals:
    def test_returnsMeals(self):
        from app.services.nutrition.get_Meals import get_meals
        with patch(f"{GET_MEALS_SVC}.run_query", return_value=[FAKE_MEAL]):
            result = get_meals()
        assert len(result) == 1
        assert result[0]["name"] == "Oatmeal"

    def test_returnsEmptyList(self):
        from app.services.nutrition.get_Meals import get_meals
        with patch(f"{GET_MEALS_SVC}.run_query", return_value=[]):
            result = get_meals()
        assert result == []


class TestGetTodaysMeals:
    def test_returnsMeals(self):
        from app.services.nutrition.get_Todays_Meals import get_todays_meals
        row = {**FAKE_MEAL, "meal_type": "breakfast", "servings": 1, "day_of_week": "Mon"}
        with patch(f"{TODAYS_SVC}.run_query", return_value=[row]):
            result = get_todays_meals(user_id=2, meal_plan_id=1)
        assert len(result) == 1

    def test_returnsEmptyList(self):
        from app.services.nutrition.get_Todays_Meals import get_todays_meals
        with patch(f"{TODAYS_SVC}.run_query", return_value=[]):
            result = get_todays_meals(user_id=2, meal_plan_id=999)
        assert result == []


class TestGetWeekMonday:
    def test_returnsMonday(self):
        from app.services.nutrition.get_Weekly_Calories import get_week_monday
        wednesday = datetime(2024, 6, 5)
        result = get_week_monday(wednesday)
        assert result.weekday() == 0
        assert result.day == 3

    def test_mondayReturnsItself(self):
        from app.services.nutrition.get_Weekly_Calories import get_week_monday
        monday = datetime(2024, 6, 3)
        result = get_week_monday(monday)
        assert result.day == 3


class TestGetWeeklyCalories:
    def test_returnsStructureWithNoMeals(self):
        from app.services.nutrition.get_Weekly_Calories import get_weekly_calories
        with patch(f"{WEEKLY_SVC}.mealLogging.getLoggedMeals", return_value=[]):
            with patch(f"{WEEKLY_SVC}.getNutritionGoals", return_value=None):
                result = get_weekly_calories(user_id=2)
        assert result["message"] == "success"
        assert len(result["days"]) == 7
        assert result["averageDailyCalories"] == 0

    def test_returnsCaloriesWithMeals(self):
        from app.services.nutrition.get_Weekly_Calories import get_weekly_calories
        with patch(f"{WEEKLY_SVC}.mealLogging.getLoggedMeals", return_value=[FAKE_LOGGED_MEAL]):
            with patch(f"{WEEKLY_SVC}.getNutritionGoals", return_value={"calories_target": 2000}):
                result = get_weekly_calories(user_id=2)
        assert result["goalCalories"] == 2000
        assert result["message"] == "success"


class TestGetMealType:
    def test_breakfast(self):
        from app.services.nutrition.get_Nutrition_Today import _get_meal_type
        assert _get_meal_type("2024-06-01T08:00:00") == "Breakfast"

    def test_lunch(self):
        from app.services.nutrition.get_Nutrition_Today import _get_meal_type
        assert _get_meal_type("2024-06-01T12:00:00") == "Lunch"

    def test_snack(self):
        from app.services.nutrition.get_Nutrition_Today import _get_meal_type
        assert _get_meal_type("2024-06-01T15:30:00") == "Snack"

    def test_dinner(self):
        from app.services.nutrition.get_Nutrition_Today import _get_meal_type
        assert _get_meal_type("2024-06-01T19:00:00") == "Dinner"


class TestFormatTimeLabel:
    def test_formatsCorrectly(self):
        from app.services.nutrition.get_Nutrition_Today import _format_time_label
        result = _format_time_label("2024-06-01T08:30:00")
        assert "8:30" in result


class TestGetNutritionToday:
    def test_returnsStructureWithNoMeals(self):
        from app.services.nutrition.get_Nutrition_Today import get_nutrition_today
        with patch(f"{NUTRITION_SVC}.mealLogging.getLoggedMeals", return_value=[]):
            with patch(f"{NUTRITION_SVC}.getNutritionGoals", return_value=None):
                result = get_nutrition_today(user_id=2)
        assert result["message"] == "success"
        assert result["calories"]["current"] == 0
        assert result["meals"] == []

    def test_returnsWithMeals(self):
        from app.services.nutrition.get_Nutrition_Today import get_nutrition_today
        with patch(f"{NUTRITION_SVC}.mealLogging.getLoggedMeals", return_value=[FAKE_LOGGED_MEAL]):
            with patch(f"{NUTRITION_SVC}.getNutritionGoals", return_value={
                "calories_target": 2000, "protein_target": 150,
                "carbs_target": 250, "fat_target": 65,
            }):
                result = get_nutrition_today(user_id=2)
        assert result["calories"]["current"] == 300
        assert result["calories"]["goal"] == 2000
        assert len(result["meals"]) == 1

    def test_foodItemMealType(self):
        from app.services.nutrition.get_Nutrition_Today import get_nutrition_today
        food_meal = {**FAKE_LOGGED_MEAL, "meal_id": None, "food_item_id": 1}
        with patch(f"{NUTRITION_SVC}.mealLogging.getLoggedMeals", return_value=[food_meal]):
            with patch(f"{NUTRITION_SVC}.getNutritionGoals", return_value=None):
                result = get_nutrition_today(user_id=2)
        assert result["meals"][0]["meal_type"] == "Food"


class TestGetMealsRoute:
    def test_unauthorized(self, client):
        res = client.get("/nutrition/meals")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{GET_MEALS_ROUTE}.get_meals", return_value=[FAKE_MEAL]):
            res = auth_client.get("/nutrition/meals")
        assert res.status_code == 200


class TestGetTodaysMealsRoute:
    def test_unauthorized(self, client):
        res = client.post("/nutrition/meal-plans/today", json={})
        assert res.status_code == 401

    def test_missingMealPlanId(self, auth_client):
        res = auth_client.post("/nutrition/meal-plans/today", json={})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{TODAYS_ROUTE}.get_todays_meals", return_value=[FAKE_MEAL]):
            res = auth_client.post("/nutrition/meal-plans/today", json={"meal_plan_id": 1})
        assert res.status_code == 200


class TestGetWeeklyCaloriesSummaryRoute:
    def test_unauthorized(self, client):
        res = client.get("/nutrition/getWeeklyCaloriesSummary")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{WEEKLY_ROUTE}.get_weekly_calories", return_value={
            "message": "success", "days": [], "averageDailyCalories": 0,
            "bestDayCalories": 0, "goalCalories": None,
        }):
            res = auth_client.get("/nutrition/getWeeklyCaloriesSummary")
        assert res.status_code == 200

    def test_serviceError(self, auth_client):
        with patch(f"{WEEKLY_ROUTE}.get_weekly_calories", side_effect=Exception("DB error")):
            res = auth_client.get("/nutrition/getWeeklyCaloriesSummary")
        assert res.status_code == 500


class TestGetNutritionTodayRoute:
    def test_unauthorized(self, client):
        res = client.get("/nutrition/getNutritionToday")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{NUTRITION_ROUTE}.get_nutrition_today", return_value={
            "message": "success", "calories": {"current": 0, "goal": None},
            "macros": {}, "meals": [],
        }):
            res = auth_client.get("/nutrition/getNutritionToday")
        assert res.status_code == 200

    def test_serviceError(self, auth_client):
        with patch(f"{NUTRITION_ROUTE}.get_nutrition_today", side_effect=Exception("error")):
            res = auth_client.get("/nutrition/getNutritionToday")
        assert res.status_code == 500