"""
tests/test_delete_meal_plan.py

Covers:
  - app/services/nutrition/deleteMealPlan.py
  - app/routes/activityLog/delete_Meal_Plan.py
"""

import pytest
from unittest.mock import patch


class TestDeleteMealPlanRoutes:
    def test_unauthorized(self, client):
        res = client.delete("nutrition/meal-plans/delete")
        assert res.status_code == 401

    def test_missingMealPlanID(self, auth_client):
        res = auth_client.delete("/nutrition/meal-plans/delete", json={})
        assert res.status_code == 400

    def test_permissionError(self, auth_client):
        with patch("app.routes.nutrition.deleteMealPlan.delete_meal_plan", side_effect = PermissionError("You are not the owner of this meal plan.")):
            res = auth_client.delete("/nutrition/meal-plans/delete", json ={"meal_plan_id": 1})
            assert res.status_code == 403 
    
    def test_Exception(self, auth_client):
        with patch("app.routes.nutrition.deleteMealPlan.delete_meal_plan", side_effect = Exception("You have an error")):
            res = auth_client.delete("/nutrition/meal-plans/delete", json={"meal_plan_id": 1})
            assert res.status_code == 500

    def test_success(self, auth_client):
        with patch("app.routes.nutrition.deleteMealPlan.delete_meal_plan", return_value=None):
            res = auth_client.delete("/nutrition/meal-plans/delete", json={"meal_plan_id": 1})
            assert res.status_code == 200

class TestDeleteMealPlanServices:
    def test_mealPlanNotFound(self):
        from app.services.nutrition.delete_Meal_Plan import delete_meal_plan
        with patch("app.services.nutrition.delete_Meal_Plan.run_query", return_value = []):
            with pytest.raises(PermissionError):
                delete_meal_plan(user_id = 2, meal_plan_id = 289)
    
    def test_mealPlanDeleted(self, mock_run_query):
        from app.services.nutrition.delete_Meal_Plan import delete_meal_plan
        with patch("app.services.nutrition.delete_Meal_Plan.run_query", side_effect=[[{"meal_plan_id": 12}], None]):
            delete_meal_plan(user_id=2, meal_plan_id=12)
            