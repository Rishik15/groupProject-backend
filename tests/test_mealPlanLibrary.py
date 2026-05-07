# Routes: /nutrition — getMealPlans.py, getMyMealPlans.py, createFoodItem.py
# Services: app/services/nutrition — get_Meal_Plans.py, get_My_Meal_Plans.py, create_Food_Item.py
# Utility: app/utils/Contract/getClientId.py

from unittest.mock import patch, MagicMock

GET_PLANS_SVC = "app.services.nutrition.get_Meal_Plans"
MY_PLANS_SVC = "app.services.nutrition.get_My_Meal_Plans"
CREATE_SVC = "app.services.nutrition.create_Food_Item"
CLIENT_ID_SVC = "app.utils.Contract.getClientId"

GET_PLANS_ROUTE = "app.routes.nutrition.getMealPlans"
MY_PLANS_ROUTE = "app.routes.nutrition.getMyMealPlans"
CREATE_ROUTE = "app.routes.nutrition.createFoodItem"

FAKE_PLAN = {"meal_plan_id": 1, "plan_name": "Bulk Plan", "total_calories": 2500}


class TestGetClientIdFromContract:
    def test_returnsClientId(self):
        from app.utils.Contract.getClientId import getClientIdFromContract
        with patch(f"{CLIENT_ID_SVC}.run_query", return_value=[{"client_id": 2}]):
            result = getClientIdFromContract(contract_id=1, coach_id=3)
        assert result == 2

    def test_returnsNoneWhenNotFound(self):
        from app.utils.Contract.getClientId import getClientIdFromContract
        with patch(f"{CLIENT_ID_SVC}.run_query", return_value=[]):
            result = getClientIdFromContract(contract_id=999, coach_id=3)
        assert result is None


class TestGetMealPlanLibrary:
    def test_returnsPlans(self):
        from app.services.nutrition.get_Meal_Plans import get_meal_plan_library
        with patch(f"{GET_PLANS_SVC}.run_query", return_value=[FAKE_PLAN]):
            result = get_meal_plan_library()
        assert len(result) == 1
        assert result[0]["plan_name"] == "Bulk Plan"

    def test_returnsEmptyList(self):
        from app.services.nutrition.get_Meal_Plans import get_meal_plan_library
        with patch(f"{GET_PLANS_SVC}.run_query", return_value=[]):
            result = get_meal_plan_library()
        assert result == []


class TestGetMyMealPlans:
    def test_returnsPlans(self):
        from app.services.nutrition.get_My_Meal_Plans import get_my_meal_plans
        with patch(f"{MY_PLANS_SVC}.run_query", return_value=[FAKE_PLAN]):
            result = get_my_meal_plans(user_id=2)
        assert len(result) == 1

    def test_returnsEmptyList(self):
        from app.services.nutrition.get_My_Meal_Plans import get_my_meal_plans
        with patch(f"{MY_PLANS_SVC}.run_query", return_value=[]):
            result = get_my_meal_plans(user_id=2)
        assert result == []


class TestCreateFoodItem:
    def test_success(self):
        from app.services.nutrition.create_Food_Item import create_food_item
        with patch(f"{CREATE_SVC}.run_query", return_value=None):
            create_food_item(user_id=2, name="Chicken", calories=200,
                             protein=30.0, carbs=5.0, fats=10.0)

    def test_successWithImageUrl(self):
        from app.services.nutrition.create_Food_Item import create_food_item
        with patch(f"{CREATE_SVC}.run_query", return_value=None):
            create_food_item(user_id=2, name="Chicken", calories=200,
                             protein=30.0, carbs=5.0, fats=10.0,
                             image_url="https://cdn.example.com/chicken.jpg")


class TestGetMealPlansRoute:
    def test_success(self, client):
        with patch(f"{GET_PLANS_ROUTE}.get_meal_plan_library", return_value=[FAKE_PLAN]):
            res = client.get("/nutrition/meal-plans")
        assert res.status_code == 200
        assert len(res.get_json()["meal_plans"]) == 1

    def test_serviceError(self, client):
        with patch(f"{GET_PLANS_ROUTE}.get_meal_plan_library", side_effect=Exception("DB error")):
            res = client.get("/nutrition/meal-plans")
        assert res.status_code == 500


class TestGetMyMealPlansRoute:
    def test_unauthorized(self, client):
        res = client.get("/nutrition/meal-plans/my-plans")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(f"{MY_PLANS_ROUTE}.get_my_meal_plans", return_value=[FAKE_PLAN]):
            res = auth_client.get("/nutrition/meal-plans/my-plans")
        assert res.status_code == 200


class TestCreateFoodItemRoute:
    def test_unauthorized(self, client):
        res = client.post("/nutrition/food-items/create", data={})
        assert res.status_code == 401

    def test_missingName(self, auth_client):
        res = auth_client.post("/nutrition/food-items/create", data={
            "calories": "200", "protein": "30", "carbs": "5", "fats": "10"
        })
        assert res.status_code == 400

    def test_missingCalories(self, auth_client):
        res = auth_client.post("/nutrition/food-items/create", data={
            "name": "Chicken", "protein": "30", "carbs": "5", "fats": "10"
        })
        assert res.status_code == 400

    def test_missingProtein(self, auth_client):
        res = auth_client.post("/nutrition/food-items/create", data={
            "name": "Chicken", "calories": "200", "carbs": "5", "fats": "10"
        })
        assert res.status_code == 400

    def test_missingCarbs(self, auth_client):
        res = auth_client.post("/nutrition/food-items/create", data={
            "name": "Chicken", "calories": "200", "protein": "30", "fats": "10"
        })
        assert res.status_code == 400

    def test_missingFats(self, auth_client):
        res = auth_client.post("/nutrition/food-items/create", data={
            "name": "Chicken", "calories": "200", "protein": "30", "carbs": "5"
        })
        assert res.status_code == 400

    def test_duplicateEntry(self, auth_client):
        with patch(f"{CREATE_ROUTE}.create_food_item", side_effect=Exception("Duplicate entry")):
            res = auth_client.post("/nutrition/food-items/create", data={
                "name": "Chicken", "calories": "200", "protein": "30",
                "carbs": "5", "fats": "10"
            })
        assert res.status_code == 409

    def test_success(self, auth_client):
        with patch(f"{CREATE_ROUTE}.create_food_item", return_value=None):
            res = auth_client.post("/nutrition/food-items/create", data={
                "name": "Chicken", "calories": "200", "protein": "30",
                "carbs": "5", "fats": "10"
            })
        assert res.status_code == 201

    def test_successWithImageUpload(self, auth_client):
        mock_file = MagicMock()
        with patch(f"{CREATE_ROUTE}.save_meal_image_for_user", return_value={"photo_url": "https://cdn.example.com/img.jpg"}):
            with patch(f"{CREATE_ROUTE}.create_food_item", return_value=None):
                res = auth_client.post("/nutrition/food-items/create", data={
                    "name": "Chicken", "calories": "200", "protein": "30",
                    "carbs": "5", "fats": "10", "image": (mock_file, "chicken.jpg")
                })
        assert res.status_code == 201