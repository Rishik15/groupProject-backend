from unittest.mock import patch
from datetime import date, time

ROUTE = "app.routes.manageClient.workouts.workoutRoutes"
GET_CLIENT = f"{ROUTE}.getClientIdFromContract"
MY_WORKOUTS = "app.services.workouts.my_Workouts"
PLAN_DAYS = "app.services.workouts.workoutPlanDays"
ASSIGN = "app.services.workouts.assign_Plan"
PREDEF = "app.services.workouts.predefined_Plans"

FAKE_PLAN = {
    "plan_id": 5,
    "plan_name": "Push Day",
    "description": "Strength | 3 days/week | 60 min | Intermediate",
    "source": "authored",
    "total_exercises": 6,
}

FAKE_DAY = {
    "day_id": 3,
    "plan_id": 5,
    "day_order": 1,
    "day_label": "Day 1",
    "total_exercises": 6,
}

FAKE_EVENT = {
    "id": "1",
    "eventId": 1,
    "userId": 2,
    "title": "Push Day",
    "date": "2024-06-01",
    "startTime": "09:00:00",
    "endTime": "10:00:00",
    "eventType": "workout",
    "description": "Push Day",
    "notes": "",
    "workoutPlanId": 5,
    "workoutDayId": 3,
    "workoutPlanName": "Push Day",
    "workoutDayLabel": "Day 1",
    "workoutDayOrder": 1,
}


class TestGetUserWorkouts:
    def test_returnsWorkouts(self):
        from app.services.workouts.my_Workouts import get_user_workouts
        with patch(f"{MY_WORKOUTS}.run_query", return_value=[FAKE_PLAN]):
            result = get_user_workouts(user_id=2)
        assert len(result) == 1
        assert result[0]["plan_name"] == "Push Day"

    def test_returnsEmptyList(self):
        from app.services.workouts.my_Workouts import get_user_workouts
        with patch(f"{MY_WORKOUTS}.run_query", return_value=[]):
            result = get_user_workouts(user_id=2)
        assert result == []


class TestGetWorkoutPlanDays:
    def test_returnsDays(self):
        from app.services.workouts.workoutPlanDays import get_workout_plan_days
        with patch(f"{PLAN_DAYS}.run_query", return_value=[FAKE_DAY]):
            result = get_workout_plan_days(user_id=2, plan_id=5)
        assert len(result) == 1
        assert result[0]["day_label"] == "Day 1"

    def test_returnsEmptyList(self):
        from app.services.workouts.workoutPlanDays import get_workout_plan_days
        with patch(f"{PLAN_DAYS}.run_query", return_value=None):
            result = get_workout_plan_days(user_id=2, plan_id=999)
        assert result == []


class TestAssignPlanToUser:
    def test_returnsSuccess(self):
        from app.services.workouts.assign_Plan import assign_plan_to_user
        with patch(f"{ASSIGN}.run_query", return_value=None):
            result = assign_plan_to_user(user_id=2, plan_id=5, coach_id=3)
        assert result["success"] is True
        assert result["planId"] == 5

    def test_usesDefaultNote(self):
        from app.services.workouts.assign_Plan import assign_plan_to_user
        with patch(f"{ASSIGN}.run_query", return_value=None):
            result = assign_plan_to_user(user_id=2, plan_id=5)
        assert result["success"] is True


class TestGetPredefinedPlans:
    def test_returnsPlans(self):
        from app.services.workouts.predefined_Plans import get_predefined_plans
        with patch(f"{PREDEF}.run_query", return_value=[FAKE_PLAN]):
            result = get_predefined_plans()
        assert len(result) == 1

    def test_withFilters(self):
        from app.services.workouts.predefined_Plans import get_predefined_plans
        with patch(f"{PREDEF}.run_query", return_value=[FAKE_PLAN]):
            result = get_predefined_plans(category="Strength", days_per_week=3)
        assert len(result) == 1

    def test_returnsEmptyList(self):
        from app.services.workouts.predefined_Plans import get_predefined_plans
        with patch(f"{PREDEF}.run_query", return_value=[]):
            result = get_predefined_plans()
        assert result == []


class TestGetEventsRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/events?contract_id=1&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.get("/manage/workouts/events?start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 400

    def test_clientNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.get("/manage/workouts/events?contract_id=99&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 404

    def test_missingDates(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.get("/manage/workouts/events?contract_id=1")
        assert res.status_code == 400

    def test_invalidDate(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.get("/manage/workouts/events?contract_id=1&start_date=bad&end_date=2024-06-07")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_events_for_user_range", return_value=[FAKE_EVENT]):
                res = coach_client.get("/manage/workouts/events?contract_id=1&start_date=2024-06-01&end_date=2024-06-07")
        assert res.status_code == 200


class TestCreateEventRoute:
    def test_unauthorized(self, client):
        res = client.post("/manage/workouts/events", json={})
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.post("/manage/workouts/events", json={})
        assert res.status_code == 400

    def test_clientNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.post("/manage/workouts/events", json={"contract_id": 99})
        assert res.status_code == 404

    def test_missingRequiredField(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/manage/workouts/events", json={
                "contract_id": 1,
                "event_date": "2024-06-01",
                "start_time": "09:00",
                "end_time": "10:00",
                "description": "Push Day",
                "workout_plan_id": 5,
            })
        assert res.status_code == 400

    def test_invalidPlanDay(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
                res = coach_client.post("/manage/workouts/events", json={
                    "contract_id": 1,
                    "event_date": "2024-06-01",
                    "start_time": "09:00",
                    "end_time": "10:00",
                    "description": "Push Day",
                    "workout_plan_id": 5,
                    "workout_day_id": 999,
                })
        assert res.status_code == 403

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
                with patch(f"{ROUTE}.create_event", return_value=FAKE_EVENT):
                    res = coach_client.post("/manage/workouts/events", json={
                        "contract_id": 1,
                        "event_date": "2024-06-01",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "description": "Push Day",
                        "workout_plan_id": 5,
                        "workout_day_id": 3,
                    })
        assert res.status_code == 201


class TestUpdateEventRoute:
    def test_unauthorized(self, client):
        res = client.patch("/manage/workouts/events", json={})
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.patch("/manage/workouts/events", json={})
        assert res.status_code == 400

    def test_missingEventId(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.patch("/manage/workouts/events", json={
                "contract_id": 1,
                "event_date": "2024-06-01",
                "start_time": "09:00",
                "end_time": "10:00",
                "description": "Push Day",
                "workout_plan_id": 5,
                "workout_day_id": 3,
            })
        assert res.status_code == 400

    def test_eventNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
                with patch(f"{ROUTE}.update_event", return_value=None):
                    res = coach_client.patch("/manage/workouts/events", json={
                        "contract_id": 1,
                        "event_id": 999,
                        "event_date": "2024-06-01",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "description": "Push Day",
                        "workout_plan_id": 5,
                        "workout_day_id": 3,
                    })
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
                with patch(f"{ROUTE}.update_event", return_value=FAKE_EVENT):
                    res = coach_client.patch("/manage/workouts/events", json={
                        "contract_id": 1,
                        "event_id": 1,
                        "event_date": "2024-06-01",
                        "start_time": "09:00",
                        "end_time": "10:00",
                        "description": "Push Day",
                        "workout_plan_id": 5,
                        "workout_day_id": 3,
                    })
        assert res.status_code == 200


class TestDeleteEventRoute:
    def test_unauthorized(self, client):
        res = client.delete("/manage/workouts/events?contract_id=1&event_id=1")
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.delete("/manage/workouts/events?event_id=1")
        assert res.status_code == 400

    def test_clientNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.delete("/manage/workouts/events?contract_id=99&event_id=1")
        assert res.status_code == 404

    def test_missingEventId(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.delete("/manage/workouts/events?contract_id=1")
        assert res.status_code == 400

    def test_eventNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.delete_event", return_value=False):
                res = coach_client.delete("/manage/workouts/events?contract_id=1&event_id=999")
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.delete_event", return_value=True):
                res = coach_client.delete("/manage/workouts/events?contract_id=1&event_id=1")
        assert res.status_code == 200


class TestGetClientPlansRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/client-plans?contract_id=1")
        assert res.status_code == 401

    def test_clientNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.get("/manage/workouts/client-plans?contract_id=99")
        assert res.status_code == 404

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_user_workouts", return_value=[FAKE_PLAN]):
                res = coach_client.get("/manage/workouts/client-plans?contract_id=1")
        assert res.status_code == 200


class TestGetCoachPlansRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/coach-plans")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.get_user_workouts", return_value=[FAKE_PLAN]):
            res = coach_client.get("/manage/workouts/coach-plans")
        assert res.status_code == 200


class TestGetPlanDaysRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/plan-days?contract_id=1&plan_id=5")
        assert res.status_code == 401

    def test_missingPlanId(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.get("/manage/workouts/plan-days?contract_id=1")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
                res = coach_client.get("/manage/workouts/plan-days?contract_id=1&plan_id=5")
        assert res.status_code == 200


class TestGetCoachPlanDaysRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/coach-plan-days?plan_id=5")
        assert res.status_code == 401

    def test_missingPlanId(self, coach_client):
        res = coach_client.get("/manage/workouts/coach-plan-days")
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.get_workout_plan_days", return_value=[FAKE_DAY]):
            res = coach_client.get("/manage/workouts/coach-plan-days?plan_id=5")
        assert res.status_code == 200


class TestAssignPlanRoute:
    def test_unauthorized(self, client):
        res = client.post("/manage/workouts/assign-plan", json={})
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.post("/manage/workouts/assign-plan", json={})
        assert res.status_code == 400

    def test_clientNotFound(self, coach_client):
        with patch(GET_CLIENT, return_value=None):
            res = coach_client.post("/manage/workouts/assign-plan", json={"contract_id": 99})
        assert res.status_code == 404

    def test_missingPlanId(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            res = coach_client.post("/manage/workouts/assign-plan", json={"contract_id": 1})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(GET_CLIENT, return_value=2):
            with patch(f"{ROUTE}.assign_plan_to_user", return_value={"success": True, "planId": 5}):
                res = coach_client.post("/manage/workouts/assign-plan", json={
                    "contract_id": 1,
                    "plan_id": 5,
                })
        assert res.status_code == 200


class TestGetSystemPlansRoute:
    def test_unauthorized(self, client):
        res = client.get("/manage/workouts/system-plans")
        assert res.status_code == 401

    def test_success(self, coach_client):
        plan = {
            "plan_id": 1,
            "plan_name": "Full Body",
            "description": "Strength | 3 days/week | 60 min | Beginner",
            "exercise_count": 12,
        }
        with patch(f"{ROUTE}.get_predefined_plans", return_value=[plan]):
            res = coach_client.get("/manage/workouts/system-plans")
        assert res.status_code == 200
        data = res.get_json()
        assert data[0]["source"] == "system"
        assert data[0]["total_exercises"] == 12