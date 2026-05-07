from unittest.mock import patch

EXERCISES_SVC = "app.services.workouts.exercises_In_Plan"
MY_WORKOUTS_SVC = "app.services.workouts.my_Workouts"
PLAN_DAYS_SVC = "app.services.workouts.workoutPlanDays"
PREDEFINED_SVC = "app.services.workouts.predefined_Plans"
ASSIGN_SVC = "app.services.workouts.assign_Plan"
CREATE_SVC = "app.services.workouts.createWorkout_Plan"

EXERCISES_ROUTE = "app.routes.workouts.exercisesInPlan"
MY_WORKOUTS_ROUTE = "app.routes.workouts.myWorkouts"
PLAN_DAYS_ROUTE = "app.routes.workouts.planDays"
PREDEFINED_ROUTE = "app.routes.workouts.predefinedPlans"
ASSIGN_ROUTE = "app.routes.workouts.assignPlan"
CREATE_ROUTE = "app.routes.workouts.createWorkoutPlan"

FAKE_DAY = {
    "day_id": 1,
    "day_order": 1,
    "day_label": "Day 1",
    "exercises": [
        {
            "exercise_id": 1,
            "exercise_name": "Bench Press",
            "equipment": "Barbell",
            "video_url": None,
            "sets_goal": 3,
            "reps_goal": 10,
            "weight_goal": 100.0,
            "order_in_workout": 1,
        }
    ],
}

FAKE_WORKOUT = {
    "plan_id": 1,
    "plan_name": "Push Day",
    "description": "Upper body",
    "source": "authored",
    "total_exercises": 3,
}

FAKE_PLAN = {
    "plan_id": 1,
    "plan_name": "Beginner Full Body",
    "category": "strength",
    "days_per_week": 3,
}


class TestGetWorkoutPlanExercises:
    def test_returnsGroupedDays(self):
        from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises

        row = {
            "day_id": 1,
            "day_order": 1,
            "day_label": "Day 1",
            "exercise_id": 1,
            "exercise_name": "Bench Press",
            "equipment": "Barbell",
            "video_url": None,
            "sets_goal": 3,
            "reps_goal": 10,
            "weight_goal": 100.0,
            "order_in_workout": 1,
        }
        with patch(f"{EXERCISES_SVC}.run_query", return_value=[row]):
            result = get_workout_plan_exercises(plan_id=1)
        assert len(result) == 1
        assert result[0]["day_label"] == "Day 1"
        assert len(result[0]["exercises"]) == 1

    def test_returnsEmptyList(self):
        from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises

        with patch(f"{EXERCISES_SVC}.run_query", return_value=[]):
            result = get_workout_plan_exercises(plan_id=999)
        assert result == []

    def test_skipsNullExercise(self):
        from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises

        row = {
            "day_id": 1,
            "day_order": 1,
            "day_label": "Day 1",
            "exercise_id": None,
            "exercise_name": None,
            "equipment": None,
            "video_url": None,
            "sets_goal": None,
            "reps_goal": None,
            "weight_goal": None,
            "order_in_workout": None,
        }
        with patch(f"{EXERCISES_SVC}.run_query", return_value=[row]):
            result = get_workout_plan_exercises(plan_id=1)
        assert len(result) == 1
        assert result[0]["exercises"] == []

    def test_fallbackDayLabel(self):
        from app.services.workouts.exercises_In_Plan import get_workout_plan_exercises

        row = {
            "day_id": 1,
            "day_order": 2,
            "day_label": None,
            "exercise_id": None,
            "exercise_name": None,
            "equipment": None,
            "video_url": None,
            "sets_goal": None,
            "reps_goal": None,
            "weight_goal": None,
            "order_in_workout": None,
        }
        with patch(f"{EXERCISES_SVC}.run_query", return_value=[row]):
            result = get_workout_plan_exercises(plan_id=1)
        assert result[0]["day_label"] == "Day 2"


class TestGetUserWorkouts:
    def test_returnsWorkouts(self):
        from app.services.workouts.my_Workouts import get_user_workouts

        with patch(f"{MY_WORKOUTS_SVC}.run_query", return_value=[FAKE_WORKOUT]):
            result = get_user_workouts(user_id=2)
        assert len(result) == 1
        assert result[0]["plan_name"] == "Push Day"

    def test_returnsEmptyList(self):
        from app.services.workouts.my_Workouts import get_user_workouts

        with patch(f"{MY_WORKOUTS_SVC}.run_query", return_value=[]):
            result = get_user_workouts(user_id=2)
        assert result == []


class TestGetPlanExercisesRoute:
    def test_missingPlanId(self, client):
        res = client.get("/workouts/workout-plan/exercises")
        assert res.status_code == 400

    def test_success(self, client):
        with patch(
            f"{EXERCISES_ROUTE}.get_workout_plan_exercises", return_value=[FAKE_DAY]
        ):
            res = client.get("/workouts/workout-plan/exercises?plan_id=1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["day_count"] == 1
        assert data["exercise_count"] == 1

    def test_serviceError(self, client):
        with patch(
            f"{EXERCISES_ROUTE}.get_workout_plan_exercises",
            side_effect=Exception("DB error"),
        ):
            res = client.get("/workouts/workout-plan/exercises?plan_id=1")
        assert res.status_code == 500


class TestMyWorkoutsRoute:
    def test_unauthorized(self, client):
        res = client.get("/workouts/my-workouts")
        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(
            f"{MY_WORKOUTS_ROUTE}.get_user_workouts", return_value=[FAKE_WORKOUT]
        ):
            res = auth_client.get("/workouts/my-workouts")
        assert res.status_code == 200
        assert res.get_json()["message"] == "success"
        assert len(res.get_json()["workouts"]) == 1


class TestPlanDaysRoute:
    def test_unauthorized(self, client):
        res = client.get("/workouts/plan-days?plan_id=1")
        assert res.status_code == 401

    def test_missingPlanId(self, auth_client):
        res = auth_client.get("/workouts/plan-days")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{PLAN_DAYS_ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
            res = auth_client.get("/workouts/plan-days?plan_id=1")
        assert res.status_code == 200
        assert res.get_json()["message"] == "success"


class TestPredefinedPlansRoute:
    def test_success(self, client):
        with patch(
            f"{PREDEFINED_ROUTE}.get_predefined_plans", return_value=[FAKE_PLAN]
        ):
            res = client.post("/workouts/predefined", json={})
        assert res.status_code == 200
        assert len(res.get_json()["plans"]) == 1

    def test_withFilters(self, client):
        with patch(
            f"{PREDEFINED_ROUTE}.get_predefined_plans", return_value=[FAKE_PLAN]
        ):
            res = client.post(
                "/workouts/predefined",
                json={
                    "category": "strength",
                    "days_per_week": 3,
                    "duration": 8,
                    "level": "beginner",
                },
            )
        assert res.status_code == 200

    def test_serviceError(self, client):
        with patch(
            f"{PREDEFINED_ROUTE}.get_predefined_plans", side_effect=Exception("error")
        ):
            res = client.post("/workouts/predefined", json={})
        assert res.status_code == 500


class TestAssignPlanRoute:
    def test_unauthorized(self, client):
        res = client.post("/workouts/predefined/assign", json={"plan_id": 1})
        assert res.status_code == 401

    def test_missingPlanId(self, auth_client):
        res = auth_client.post("/workouts/predefined/assign", json={})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ASSIGN_ROUTE}.assign_plan_to_user", return_value=None):
            res = auth_client.post("/workouts/predefined/assign", json={"plan_id": 1})
        assert res.status_code == 201


class TestCreateWorkoutPlanRoute:
    def test_unauthorized(self, client):
        res = client.post("/workouts/create", json={"name": "My Plan", "days": []})
        assert res.status_code == 401

    def test_missingPlanName(self, auth_client):
        res = auth_client.post(
            "/workouts/create", json={"days": [{"exercises": [{"exercise_id": 1}]}]}
        )
        assert res.status_code == 400

    def test_noDays(self, auth_client):
        res = auth_client.post("/workouts/create", json={"name": "My Plan", "days": []})
        assert res.status_code == 400

    def test_dayWithNoExercises(self, auth_client):
        res = auth_client.post(
            "/workouts/create",
            json={"name": "My Plan", "days": [{"day_label": "Day 1", "exercises": []}]},
        )
        assert res.status_code == 400

    def test_success(self, auth_client):
        fake_user = [{"first_name": "Alex", "last_name": "Smith"}]
        with patch(f"{CREATE_ROUTE}.run_query", return_value=fake_user):
            with patch(f"{CREATE_ROUTE}.create_workout_plan", return_value=1):
                res = auth_client.post(
                    "/workouts/create",
                    json={
                        "name": "My Plan",
                        "days": [
                            {
                                "day_label": "Day 1",
                                "exercises": [
                                    {"exercise_id": 1, "sets": 3, "reps": 10}
                                ],
                            }
                        ],
                    },
                )
        assert res.status_code == 201
        assert res.get_json()["plan_id"] == 1
