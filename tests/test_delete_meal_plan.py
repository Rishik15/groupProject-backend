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

