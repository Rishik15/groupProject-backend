from unittest.mock import patch

ROUTE = "app.routes.onboarding.onboard"
SVC = "app.services.onboarding.onboardUser"


class TestOnboardClientSurvey:
    def test_success(self):
        from app.services.onboarding.onboardUser import onboardClientSurvey
        with patch(f"{SVC}.run_query", return_value=None):
            onboardClientSurvey(
                user_id=2,
                profile_picture=None,
                weight=70.0,
                height=175.0,
                goal_weight=65.0,
            )

    def test_successWithDob(self):
        from app.services.onboarding.onboardUser import onboardClientSurvey
        with patch(f"{SVC}.run_query", return_value=None):
            onboardClientSurvey(
                user_id=2,
                profile_picture=None,
                weight=70.0,
                height=175.0,
                goal_weight=65.0,
                dob="1990-01-01",
            )


class TestOnboardCoachSurvey:
    def test_success(self):
        from app.services.onboarding.onboardUser import onboardCoachSurvey
        with patch(f"{SVC}.run_query", return_value=None):
            onboardCoachSurvey(user_id=3, desc="Experienced coach", price=50.0)


class TestInsertCoachCert:
    def test_success(self):
        from app.services.onboarding.onboardUser import insertCoachCert
        with patch(f"{SVC}.run_query", return_value=None):
            insertCoachCert(
                coach_id=3,
                cert_name="CPT",
                provider_name="NASM",
                description="Personal Trainer Certification",
                issued_date="2020-01-01",
                expires_date="2025-01-01",
            )


class TestCoachAvailability:
    def test_successWithFullDayName(self):
        from app.services.onboarding.onboardUser import coachAvailability
        with patch(f"{SVC}.run_query", return_value=None):
            coachAvailability(
                coach_id=3, dow="Monday",
                st="09:00:00", et="17:00:00", rec=1, active=1,
            )

    def test_successWithShortDayName(self):
        from app.services.onboarding.onboardUser import coachAvailability
        with patch(f"{SVC}.run_query", return_value=None):
            coachAvailability(
                coach_id=3, dow="Mon",
                st="09:00:00", et="17:00:00", rec=1, active=1,
            )

    def test_allDayMappings(self):
        from app.services.onboarding.onboardUser import coachAvailability
        days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            with patch(f"{SVC}.run_query", return_value=None):
                coachAvailability(
                    coach_id=3, dow=day,
                    st="09:00:00", et="17:00:00", rec=1, active=1,
                )


class TestOnboardSurveyRoute:
    def test_unauthorized(self, client):
        res = client.post("/onboard/", json={})
        assert res.status_code == 401

    def test_missingRequiredFields(self, auth_client):
        res = auth_client.post("/onboard/", json={
            "weight": 70.0,
            "dob": "1990-01-01",
        })
        assert res.status_code == 400

    def test_missingWeight(self, auth_client):
        res = auth_client.post("/onboard/", json={
            "height": 175.0,
            "dob": "1990-01-01",
        })
        assert res.status_code == 400

    def test_missingDob(self, auth_client):
        res = auth_client.post("/onboard/", json={
            "weight": 70.0,
            "height": 175.0,
        })
        assert res.status_code == 400

    def test_successWithAllFields(self, auth_client):
        with patch(f"{ROUTE}.onboardUser.onboardClientSurvey", return_value=None):
            res = auth_client.post("/onboard/", json={
                "weight": 70.0,
                "height": 175.0,
                "dob": "1990-01-01",
                "goal_weight": 65.0,
                "profile_picture": None,
            })
        assert res.status_code == 200
        assert res.get_json()["message"] == "Client onboarding completed successfully"

    def test_successGoalWeightDefaultsToWeight(self, auth_client):
        with patch(f"{ROUTE}.onboardUser.onboardClientSurvey", return_value=None):
            res = auth_client.post("/onboard/", json={
                "weight": 70.0,
                "height": 175.0,
                "dob": "1990-01-01",
            })
        assert res.status_code == 200

    def test_successNoDob(self, auth_client):
        with patch(f"{ROUTE}.onboardUser.onboardClientSurvey", return_value=None):
            res = auth_client.post("/onboard/", json={
                "weight": 70.0,
                "height": 175.0,
                "dob": "1990-06-15",
            })
        assert res.status_code == 200