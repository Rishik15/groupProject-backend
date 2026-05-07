from unittest.mock import patch, MagicMock

SVC = "app.services.nutrition.log_Food_Item"
ROUTE = "app.routes.nutrition.logFoodItem"


class TestLogFoodItemService:
    def test_existingFoodItemUpdatesAndLogs(self):
        from app.services.nutrition.log_Food_Item import log_food_item
        with patch(f"{SVC}.run_query", side_effect=[
            [{"food_item_id": 1}],
            None,
            None,
        ]):
            result = log_food_item(
                user_id=2, name="Chicken", calories=200,
                protein=30.0, carbs=5.0, fats=10.0,
                servings=1.0, eaten_at="2024-06-01T12:00:00",
            )
        assert result["food_item_id"] == 1
        assert result["photo_url"] is None

    def test_newFoodItemInsertsAndLogs(self):
        from app.services.nutrition.log_Food_Item import log_food_item
        with patch(f"{SVC}.run_query", side_effect=[[], 5, None]):
            result = log_food_item(
                user_id=2, name="Rice", calories=150,
                protein=3.0, carbs=35.0, fats=1.0,
                servings=1.0, eaten_at="2024-06-01T12:00:00",
            )
        assert result["food_item_id"] == 5

    def test_withPhotoUpload(self):
        from app.services.nutrition.log_Food_Item import log_food_item
        mock_file = MagicMock()
        with patch(f"{SVC}.save_meal_image_for_user", return_value={"photo_url": "https://cdn.example.com/photo.jpg"}):
            with patch(f"{SVC}.run_query", side_effect=[[], 5, None]):
                result = log_food_item(
                    user_id=2, name="Salad", calories=100,
                    protein=2.0, carbs=10.0, fats=5.0,
                    servings=1.0, eaten_at="2024-06-01T12:00:00",
                    uploaded_file=mock_file,
                )
        assert result["photo_url"] == "https://cdn.example.com/photo.jpg"


class TestLogFoodItemRoute:
    def test_unauthorized(self, client):
        res = client.post("/nutrition/log-food-item", data={})
        assert res.status_code == 401

    def test_missingName(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "calories": "200", "protein": "30", "carbs": "5",
            "fats": "10", "eaten_at": "2024-06-01T12:00:00",
        })
        assert res.status_code == 400

    def test_missingCalories(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "protein": "30", "carbs": "5",
            "fats": "10", "eaten_at": "2024-06-01T12:00:00",
        })
        assert res.status_code == 400

    def test_missingProtein(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "calories": "200", "carbs": "5",
            "fats": "10", "eaten_at": "2024-06-01T12:00:00",
        })
        assert res.status_code == 400

    def test_missingCarbs(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "calories": "200", "protein": "30",
            "fats": "10", "eaten_at": "2024-06-01T12:00:00",
        })
        assert res.status_code == 400

    def test_missingFats(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "calories": "200", "protein": "30",
            "carbs": "5", "eaten_at": "2024-06-01T12:00:00",
        })
        assert res.status_code == 400

    def test_missingEatenAt(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "calories": "200", "protein": "30",
            "carbs": "5", "fats": "10",
        })
        assert res.status_code == 400

    def test_zeroServings(self, auth_client):
        res = auth_client.post("/nutrition/log-food-item", data={
            "name": "Chicken", "calories": "200", "protein": "30",
            "carbs": "5", "fats": "10", "eaten_at": "2024-06-01T12:00:00",
            "servings": "0",
        })
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.log_food_item", return_value={"food_item_id": 1, "photo_url": None}):
            res = auth_client.post("/nutrition/log-food-item", data={
                "name": "Chicken", "calories": "200", "protein": "30",
                "carbs": "5", "fats": "10", "eaten_at": "2024-06-01T12:00:00",
            })
        assert res.status_code == 201
        assert res.get_json()["food_item_id"] == 1