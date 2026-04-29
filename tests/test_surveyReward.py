# Route: /survey/daily/reward — app/routes/survey/reward.py
# Service: app/services/survey/reward.py

from unittest.mock import patch, MagicMock

SVC = "app.services.survey.reward"
ROUTE = "app.routes.survey.reward"

FAKE_USER = {"user_id": 2, "account_status": "active"}
FAKE_WALLET = {"user_id": 2, "balance": 100}


class TestGetUserRow:
    def test_returnsUser(self):
        from app.services.survey.reward import _get_user_row
        with patch(f"{SVC}.run_query", return_value=[FAKE_USER]):
            result = _get_user_row(user_id=2)
        assert result["account_status"] == "active"

    def test_userNotFound(self):
        from app.services.survey.reward import _get_user_row
        import pytest
        with patch(f"{SVC}.run_query", return_value=[]):
            with pytest.raises(ValueError, match="User not found"):
                _get_user_row(user_id=999)


class TestGetOrCreateWalletRow:
    def test_returnsExistingWallet(self):
        from app.services.survey.reward import _get_or_create_wallet_row
        with patch(f"{SVC}.run_query", return_value=[FAKE_WALLET]):
            result = _get_or_create_wallet_row(user_id=2)
        assert result["balance"] == 100

    def test_createsWalletWhenNotFound(self):
        from app.services.survey.reward import _get_or_create_wallet_row
        with patch(f"{SVC}.run_query", side_effect=[[], None, [FAKE_WALLET]]):
            result = _get_or_create_wallet_row(user_id=2)
        assert result["balance"] == 100


class TestAlreadyRewardedToday:
    def test_returnsTrueWhenRewarded(self):
        from app.services.survey.reward import _already_rewarded_today
        with patch(f"{SVC}.run_query", return_value=[{"txn_id": 1}]):
            assert _already_rewarded_today(user_id=2) is True

    def test_returnsFalseWhenNotRewarded(self):
        from app.services.survey.reward import _already_rewarded_today
        with patch(f"{SVC}.run_query", return_value=[]):
            assert _already_rewarded_today(user_id=2) is False


class TestRewardDailySurvey:
    def test_inactiveUserRaises(self):
        from app.services.survey.reward import reward_daily_survey
        import pytest
        with patch(f"{SVC}.run_query", return_value=[{"user_id": 2, "account_status": "inactive"}]):
            with pytest.raises(ValueError, match="not active"):
                reward_daily_survey(user_id=2)

    def test_alreadyAwardedToday(self):
        from app.services.survey.reward import reward_daily_survey
        with patch(f"{SVC}._get_user_row", return_value=FAKE_USER):
            with patch(f"{SVC}._get_or_create_wallet_row", return_value=FAKE_WALLET):
                with patch(f"{SVC}._already_rewarded_today", return_value=True):
                    result = reward_daily_survey(user_id=2)
        assert result["already_awarded"] is True
        assert result["points_awarded"] == 0

    def test_successFirstReward(self):
        from app.services.survey.reward import reward_daily_survey
        mock_session = MagicMock()
        with patch(f"{SVC}._get_user_row", return_value=FAKE_USER):
            with patch(f"{SVC}._get_or_create_wallet_row", return_value=FAKE_WALLET):
                with patch(f"{SVC}._already_rewarded_today", return_value=False):
                    with patch(f"{SVC}.db.session", mock_session):
                        with patch(f"{SVC}.run_query", return_value=[{"balance": 200}]):
                            result = reward_daily_survey(user_id=2)
        assert result["already_awarded"] is False
        assert result["points_awarded"] == 100
        assert result["new_balance"] == 200


class TestRewardDailySurveyRoute:
    def test_unauthorized(self, client):
        res = client.post("/survey/daily/reward")
        assert res.status_code == 401

    def test_alreadyAwarded(self, auth_client):
        with patch(f"{ROUTE}.reward_daily_survey", return_value={
            "already_awarded": True, "points_awarded": 0
        }):
            res = auth_client.post("/survey/daily/reward")
        assert res.status_code == 200
        assert res.get_json()["reward"]["already_awarded"] is True

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.reward_daily_survey", return_value={
            "already_awarded": False, "points_awarded": 100, "new_balance": 200
        }):
            res = auth_client.post("/survey/daily/reward")
        assert res.status_code == 200
        assert res.get_json()["reward"]["points_awarded"] == 100

    def test_valueError(self, auth_client):
        with patch(f"{ROUTE}.reward_daily_survey", side_effect=ValueError("User account is not active")):
            res = auth_client.post("/survey/daily/reward")
        assert res.status_code == 400