# Routes: /manage/nutrition — app/routes/manageClient/nutrition/mealPlan.py, nutritionRoutes.py
# Services: app/services/nutrition/setGoals.py, get_Nutrition_Today.py, get_Weekly_Calories.py

from unittest.mock import patch

MEAL_PLAN_ROUTE = "app.routes.manageClient.nutrition.mealPlan"
NUTRITION_ROUTE = "app.routes.manageClient.nutrition.nutritionRoutes"
GET_CLIENT = "app.utils.Contract.getClientId.getClientIdFromContract"

FAKE_GOALS = {
    "user_id": 2, "calories_target": 2000, "protein_target": 150,
    "carbs_target": 250, "fat_target": 65,
    "created_at": "2024-06-01", "updated_at": "2024-06-01",
}

FAKE_PLAN = {"meal_plan_id": 1, "plan_name": "Bulk Plan", "user_id": 2}


class TestGetMealPlansRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/nutrition/meal-plans?contract_id=1")
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.get("/manage/nutrition/meal-plans")
        assert res.status_code == 400

    def test_invalidContract(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=None):
            res = coach_client.get("/manage/nutrition/meal-plans?contract_id=999")
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.get_meal_plan_library", return_value=[FAKE_PLAN]):
                res = coach_client.get("/manage/nutrition/meal-plans?contract_id=1")
        assert res.status_code == 200
        assert "meal_plans" in res.get_json()


class TestGetMealPlanDetailRoute:
    def test_missingMealPlanId(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.get("/manage/nutrition/meal-plans/detail?contract_id=1")
        assert res.status_code == 400

    def test_accessDenied(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=False):
                res = coach_client.get("/manage/nutrition/meal-plans/detail?contract_id=1&meal_plan_id=1")
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=True):
                with patch(f"{MEAL_PLAN_ROUTE}.get_meal_plan_detail", return_value=FAKE_PLAN):
                    res = coach_client.get("/manage/nutrition/meal-plans/detail?contract_id=1&meal_plan_id=1")
        assert res.status_code == 200


class TestGetClientMealPlansRoute:
    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.get_my_meal_plans", return_value=[FAKE_PLAN]):
                res = coach_client.get("/manage/nutrition/meal-plans/my-plans?contract_id=1")
        assert res.status_code == 200


class TestCreateMealPlanRoute:
    def test_missingPlanName(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.post("/manage/nutrition/meal-plans/create?contract_id=1", json={})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.create_meal_plan", return_value=1):
                res = coach_client.post("/manage/nutrition/meal-plans/create?contract_id=1", json={
                    "plan_name": "Bulk Plan", "meals": []
                })
        assert res.status_code == 201

    def test_duplicateName(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.create_meal_plan", side_effect=Exception("Duplicate entry")):
                res = coach_client.post("/manage/nutrition/meal-plans/create?contract_id=1", json={
                    "plan_name": "Bulk Plan"
                })
        assert res.status_code == 409


class TestAssignMealPlanRoute:
    def test_missingMealPlanId(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.post("/manage/nutrition/meal-plans/assign?contract_id=1", json={})
        assert res.status_code == 400

    def test_accessDenied(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=False):
                res = coach_client.post("/manage/nutrition/meal-plans/assign?contract_id=1", json={"meal_plan_id": 1})
        assert res.status_code == 404

    def test_existingPlanConflict(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=True):
                with patch(f"{MEAL_PLAN_ROUTE}.assign_meal_plan", side_effect=ValueError("EXISTING_PLAN:Bulk Plan")):
                    res = coach_client.post("/manage/nutrition/meal-plans/assign?contract_id=1", json={"meal_plan_id": 1})
        assert res.status_code == 409

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=True):
                with patch(f"{MEAL_PLAN_ROUTE}.assign_meal_plan", return_value=1):
                    res = coach_client.post("/manage/nutrition/meal-plans/assign?contract_id=1", json={"meal_plan_id": 1})
        assert res.status_code == 201


class TestUpdateMealPlanRoute:
    def test_missingMealPlanId(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.put("/manage/nutrition/meal-plans/update?contract_id=1", json={})
        assert res.status_code == 400

    def test_accessDenied(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=False):
                res = coach_client.put("/manage/nutrition/meal-plans/update?contract_id=1", json={"meal_plan_id": 1})
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.coach_can_access_plan", return_value=True):
                with patch(f"{MEAL_PLAN_ROUTE}.update_meal_plan", return_value={"meal_plan_id": 1, "total_calories": 2000}):
                    res = coach_client.put("/manage/nutrition/meal-plans/update?contract_id=1", json={"meal_plan_id": 1})
        assert res.status_code == 200


class TestDeleteMealPlanManageRoute:
    def test_missingMealPlanId(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.delete("/manage/nutrition/meal-plans/delete?contract_id=1")
        assert res.status_code == 400

    def test_permissionError(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.delete_meal_plan", side_effect=PermissionError("Not owner")):
                res = coach_client.delete("/manage/nutrition/meal-plans/delete?contract_id=1&meal_plan_id=1")
        assert res.status_code == 403

    def test_success(self, coach_client):
        with patch(f"{MEAL_PLAN_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{MEAL_PLAN_ROUTE}.delete_meal_plan", return_value=None):
                res = coach_client.delete("/manage/nutrition/meal-plans/delete?contract_id=1&meal_plan_id=1")
        assert res.status_code == 200


class TestGetNutritionTodayContractRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/nutrition/getNutritionToday?contract_id=1")
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.get("/manage/nutrition/getNutritionToday")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{NUTRITION_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{NUTRITION_ROUTE}.get_nutrition_today", return_value={"message": "success"}):
                res = coach_client.get("/manage/nutrition/getNutritionToday?contract_id=1")
        assert res.status_code == 200


class TestGetWeeklyCaloriesContractRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/nutrition/getWeeklyCaloriesSummary?contract_id=1")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{NUTRITION_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{NUTRITION_ROUTE}.get_weekly_calories", return_value={"message": "success"}):
                res = coach_client.get("/manage/nutrition/getWeeklyCaloriesSummary?contract_id=1")
        assert res.status_code == 200


class TestGetNutritionGoalsContractRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/nutrition/goals?contract_id=1")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{NUTRITION_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{NUTRITION_ROUTE}.get_user_nutrition_goals", return_value=FAKE_GOALS):
                res = coach_client.get("/manage/nutrition/goals?contract_id=1")
        assert res.status_code == 200
        assert res.get_json()["goals"]["calories_target"] == 2000


class TestSetNutritionGoalsContractRoute:
    def test_noGoalsProvided(self, coach_client):
        with patch(f"{NUTRITION_ROUTE}.getClientIdFromContract", return_value=2):
            res = coach_client.post("/manage/nutrition/goals?contract_id=1", json={})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{NUTRITION_ROUTE}.getClientIdFromContract", return_value=2):
            with patch(f"{NUTRITION_ROUTE}.upsert_user_nutrition_goals", return_value=FAKE_GOALS):
                res = coach_client.post("/manage/nutrition/goals?contract_id=1", json={"calories_target": 2000})
        assert res.status_code == 200