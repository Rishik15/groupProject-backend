from datetime import date
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
                dob=date(1990, 1, 1),
            )

    def test_success_with_string_dob(self):
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
            onboardCoachSurvey(
                user_id=3,
                desc="Experienced coach",
                price=50.0,
            )


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
    def test_success_with_full_day_name(self):
        from app.services.onboarding.onboardUser import coachAvailability

        with patch(f"{SVC}.run_query", return_value=None):
            coachAvailability(
                coach_id=3,
                dow="Monday",
                st="09:00:00",
                et="17:00:00",
                rec=1,
                active=1,
            )

    def test_success_with_short_day_name(self):
        from app.services.onboarding.onboardUser import coachAvailability

        with patch(f"{SVC}.run_query", return_value=None):
            coachAvailability(
                coach_id=3,
                dow="Mon",
                st="09:00:00",
                et="17:00:00",
                rec=1,
                active=1,
            )

    def test_all_day_mappings(self):
        from app.services.onboarding.onboardUser import coachAvailability

        days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            with patch(f"{SVC}.run_query", return_value=None):
                coachAvailability(
                    coach_id=3,
                    dow=day,
                    st="09:00:00",
                    et="17:00:00",
                    rec=1,
                    active=1,
                )


class TestParseDate:
    def test_parse_date_from_date_string(self):
        from app.routes.onboarding.onboard import _parse_date

        result = _parse_date("1990-01-01")

        assert result == date(1990, 1, 1)

    def test_parse_date_from_datetime_string(self):
        from app.routes.onboarding.onboard import _parse_date

        result = _parse_date("1990-01-01T12:30:00")

        assert result == date(1990, 1, 1)

    def test_parse_date_invalid_returns_none(self):
        from app.routes.onboarding.onboard import _parse_date

        result = _parse_date("bad-date")

        assert result is None

    def test_parse_date_empty_returns_none(self):
        from app.routes.onboarding.onboard import _parse_date

        result = _parse_date(None)

        assert result is None


class TestOnboardSurveyRoute:
    def test_unauthorized(self, client):
        res = client.post("/onboard/", json={})

        assert res.status_code == 401

    def test_missing_required_fields(self, auth_client):
        res = auth_client.post(
            "/onboard/",
            json={
                "weight": 70.0,
                "dob": "1990-01-01",
            },
        )

        assert res.status_code == 400
        assert (
            res.get_json()["error"] == "weight, height, and date of birth are required"
        )

    def test_missing_weight(self, auth_client):
        res = auth_client.post(
            "/onboard/",
            json={
                "height": 175.0,
                "dob": "1990-01-01",
            },
        )

        assert res.status_code == 400
        assert (
            res.get_json()["error"] == "weight, height, and date of birth are required"
        )

    def test_missing_height(self, auth_client):
        res = auth_client.post(
            "/onboard/",
            json={
                "weight": 70.0,
                "dob": "1990-01-01",
            },
        )

        assert res.status_code == 400
        assert (
            res.get_json()["error"] == "weight, height, and date of birth are required"
        )

    def test_missing_dob(self, auth_client):
        res = auth_client.post(
            "/onboard/",
            json={
                "weight": 70.0,
                "height": 175.0,
            },
        )

        assert res.status_code == 400
        assert (
            res.get_json()["error"] == "weight, height, and date of birth are required"
        )

    def test_invalid_dob(self, auth_client):
        res = auth_client.post(
            "/onboard/",
            json={
                "weight": 70.0,
                "height": 175.0,
                "dob": "not-a-date",
            },
        )

        assert res.status_code == 400
        assert (
            res.get_json()["error"] == "weight, height, and date of birth are required"
        )

    def test_success_with_all_fields(self, auth_client):
        with patch(
            f"{ROUTE}.onboardUser.onboardClientSurvey",
            return_value=None,
        ) as mock:
            res = auth_client.post(
                "/onboard/",
                json={
                    "weight": 70.0,
                    "height": 175.0,
                    "dob": "1990-01-01",
                    "goal_weight": 65.0,
                    "profile_picture": None,
                },
            )

        assert res.status_code == 200
        assert res.get_json()["message"] == "Client onboarding completed successfully"

        mock.assert_called_once_with(
            user_id=2,
            profile_picture=None,
            weight=70.0,
            height=175.0,
            goal_weight=65.0,
            dob=date(1990, 1, 1),
        )

    def test_success_goal_weight_defaults_to_weight(self, auth_client):
        with patch(
            f"{ROUTE}.onboardUser.onboardClientSurvey",
            return_value=None,
        ) as mock:
            res = auth_client.post(
                "/onboard/",
                json={
                    "weight": 70.0,
                    "height": 175.0,
                    "dob": "1990-01-01",
                },
            )

        assert res.status_code == 200

        mock.assert_called_once_with(
            user_id=2,
            profile_picture=None,
            weight=70.0,
            height=175.0,
            goal_weight=70.0,
            dob=date(1990, 1, 1),
        )

    def test_success_with_datetime_dob(self, auth_client):
        with patch(
            f"{ROUTE}.onboardUser.onboardClientSurvey",
            return_value=None,
        ) as mock:
            res = auth_client.post(
                "/onboard/",
                json={
                    "weight": 70.0,
                    "height": 175.0,
                    "dob": "1990-06-15T10:30:00",
                },
            )

        assert res.status_code == 200

        mock.assert_called_once_with(
            user_id=2,
            profile_picture=None,
            weight=70.0,
            height=175.0,
            goal_weight=70.0,
            dob=date(1990, 6, 15),
        )

    def test_service_error(self, auth_client):
        with patch(
            f"{ROUTE}.onboardUser.onboardClientSurvey",
            side_effect=Exception("DB error"),
        ):
            res = auth_client.post(
                "/onboard/",
                json={
                    "weight": 70.0,
                    "height": 175.0,
                    "dob": "1990-01-01",
                },
            )

        assert res.status_code == 500
        assert res.get_json()["error"] == "DB error"
