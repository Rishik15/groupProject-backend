from datetime import date, datetime
from unittest.mock import patch

SVC = "app.services.payments.subscriptionManagementService"
ROUTE = "app.routes.payments.subscriptionManagementRoutes"

FAKE_CONTRACT_ROW = {
    "contract_id": 1,
    "coach_id": 3,
    "user_id": 2,
    "agreed_price": 75.00,
    "coach_name": "Alex Smith",
    "is_recurring": 0,
    "next_billing_date": None,
    "start_date": "2026-05-01",
    "end_date": None,
    "active": 1,
}

FAKE_RECURRING_CONTRACT_ROW = {
    **FAKE_CONTRACT_ROW,
    "is_recurring": 1,
    "next_billing_date": "2026-06-01",
}

FAKE_FORMATTED_CONTRACT = {
    "contract_id": 1,
    "coach_id": 3,
    "user_id": 2,
    "agreed_price": 75.0,
    "coach_name": "Alex Smith",
    "is_recurring": 0,
    "next_billing_date": None,
    "start_date": "2026-05-01",
    "end_date": None,
    "active": 1,
}

FAKE_FORMATTED_RECURRING_CONTRACT = {
    **FAKE_FORMATTED_CONTRACT,
    "is_recurring": 1,
    "next_billing_date": "2026-06-01",
}


class TestFormatDate:
    def test_none_returns_none(self):
        from app.services.payments.subscriptionManagementService import format_date

        assert format_date(None) is None

    def test_date_returns_iso_string(self):
        from app.services.payments.subscriptionManagementService import format_date

        assert format_date(date(2026, 5, 7)) == "2026-05-07"

    def test_datetime_returns_iso_string(self):
        from app.services.payments.subscriptionManagementService import format_date

        result = format_date(datetime(2026, 5, 7, 10, 30, 0))

        assert result == "2026-05-07T10:30:00"

    def test_string_returns_string(self):
        from app.services.payments.subscriptionManagementService import format_date

        assert format_date("2026-05-07") == "2026-05-07"


class TestFormatContract:
    def test_none_returns_none(self):
        from app.services.payments.subscriptionManagementService import format_contract

        assert format_contract(None) is None

    def test_formats_contract(self):
        from app.services.payments.subscriptionManagementService import format_contract

        result = format_contract(dict(FAKE_CONTRACT_ROW))

        assert result["contract_id"] == 1
        assert result["coach_id"] == 3
        assert result["user_id"] == 2
        assert result["agreed_price"] == 75.0
        assert result["coach_name"] == "Alex Smith"
        assert result["is_recurring"] == 0
        assert result["next_billing_date"] is None
        assert result["start_date"] == "2026-05-01"
        assert result["end_date"] is None
        assert result["active"] == 1

    def test_formats_date_objects(self):
        from app.services.payments.subscriptionManagementService import format_contract

        row = {
            **FAKE_CONTRACT_ROW,
            "start_date": date(2026, 5, 1),
            "end_date": date(2026, 6, 1),
            "next_billing_date": date(2026, 5, 30),
        }

        result = format_contract(row)

        assert result["start_date"] == "2026-05-01"
        assert result["end_date"] == "2026-06-01"
        assert result["next_billing_date"] == "2026-05-30"


class TestGetActiveClientSubscriptionContract:
    def test_returns_contract(self):
        from app.services.payments.subscriptionManagementService import (
            get_active_client_subscription_contract,
        )

        with patch(f"{SVC}.run_query", return_value=[FAKE_CONTRACT_ROW]) as mock:
            result = get_active_client_subscription_contract(user_id=2)

        assert result == FAKE_FORMATTED_CONTRACT

        mock.assert_called_once()
        args = mock.call_args.args
        kwargs = mock.call_args.kwargs

        assert "FROM user_coach_contract" in args[0]
        assert args[1]["user_id"] == 2
        assert kwargs["fetch"] is True
        assert kwargs["commit"] is False

    def test_returns_none_when_no_contract(self):
        from app.services.payments.subscriptionManagementService import (
            get_active_client_subscription_contract,
        )

        with patch(f"{SVC}.run_query", return_value=[]):
            result = get_active_client_subscription_contract(user_id=2)

        assert result is None


class TestUserHasDefaultPaymentMethod:
    def test_returns_true_when_default_exists(self):
        from app.services.payments.subscriptionManagementService import (
            user_has_default_payment_method,
        )

        with patch(
            f"{SVC}.run_query",
            return_value=[{"payment_method_id": 5}],
        ):
            result = user_has_default_payment_method(user_id=2)

        assert result is True

    def test_returns_false_when_default_missing(self):
        from app.services.payments.subscriptionManagementService import (
            user_has_default_payment_method,
        )

        with patch(f"{SVC}.run_query", return_value=[]):
            result = user_has_default_payment_method(user_id=2)

        assert result is False


class TestStartClientSubscription:
    def test_no_active_contract_raises(self):
        from app.services.payments.subscriptionManagementService import (
            start_client_subscription,
        )

        with patch(f"{SVC}.get_active_client_subscription_contract", return_value=None):
            try:
                start_client_subscription(user_id=2)
                assert False
            except ValueError as error:
                assert str(error) == "You do not have an active coach contract"

    def test_already_recurring_returns_contract(self):
        from app.services.payments.subscriptionManagementService import (
            start_client_subscription,
        )

        with patch(
            f"{SVC}.get_active_client_subscription_contract",
            return_value=FAKE_FORMATTED_RECURRING_CONTRACT,
        ):
            result = start_client_subscription(user_id=2)

        assert result == FAKE_FORMATTED_RECURRING_CONTRACT

    def test_no_default_payment_method_raises(self):
        from app.services.payments.subscriptionManagementService import (
            start_client_subscription,
        )

        with patch(
            f"{SVC}.get_active_client_subscription_contract",
            return_value=FAKE_FORMATTED_CONTRACT,
        ):
            with patch(f"{SVC}.user_has_default_payment_method", return_value=False):
                try:
                    start_client_subscription(user_id=2)
                    assert False
                except ValueError as error:
                    assert (
                        str(error)
                        == "Please add a default payment method before starting a subscription"
                    )

    def test_success_updates_and_returns_latest_contract(self):
        from app.services.payments.subscriptionManagementService import (
            start_client_subscription,
        )

        with patch(
            f"{SVC}.get_active_client_subscription_contract",
            side_effect=[
                FAKE_FORMATTED_CONTRACT,
                FAKE_FORMATTED_RECURRING_CONTRACT,
            ],
        ):
            with patch(f"{SVC}.user_has_default_payment_method", return_value=True):
                with patch(f"{SVC}.run_query", return_value=None) as mock:
                    result = start_client_subscription(user_id=2)

        assert result == FAKE_FORMATTED_RECURRING_CONTRACT

        mock.assert_called_once()
        args = mock.call_args.args
        kwargs = mock.call_args.kwargs

        assert "UPDATE user_coach_contract" in args[0]
        assert args[1]["contract_id"] == 1
        assert args[1]["user_id"] == 2
        assert kwargs["fetch"] is False
        assert kwargs["commit"] is True


class TestCancelClientSubscription:
    def test_no_active_contract_raises(self):
        from app.services.payments.subscriptionManagementService import (
            cancel_client_subscription,
        )

        with patch(f"{SVC}.get_active_client_subscription_contract", return_value=None):
            try:
                cancel_client_subscription(user_id=2)
                assert False
            except ValueError as error:
                assert str(error) == "You do not have an active coach contract"

    def test_not_recurring_returns_contract(self):
        from app.services.payments.subscriptionManagementService import (
            cancel_client_subscription,
        )

        with patch(
            f"{SVC}.get_active_client_subscription_contract",
            return_value=FAKE_FORMATTED_CONTRACT,
        ):
            result = cancel_client_subscription(user_id=2)

        assert result == FAKE_FORMATTED_CONTRACT

    def test_success_updates_and_returns_latest_contract(self):
        from app.services.payments.subscriptionManagementService import (
            cancel_client_subscription,
        )

        cancelled_contract = {
            **FAKE_FORMATTED_RECURRING_CONTRACT,
            "is_recurring": 0,
            "next_billing_date": None,
        }

        with patch(
            f"{SVC}.get_active_client_subscription_contract",
            side_effect=[
                FAKE_FORMATTED_RECURRING_CONTRACT,
                cancelled_contract,
            ],
        ):
            with patch(f"{SVC}.run_query", return_value=None) as mock:
                result = cancel_client_subscription(user_id=2)

        assert result == cancelled_contract

        mock.assert_called_once()
        args = mock.call_args.args
        kwargs = mock.call_args.kwargs

        assert "UPDATE user_coach_contract" in args[0]
        assert args[1]["contract_id"] == 1
        assert args[1]["user_id"] == 2
        assert kwargs["fetch"] is False
        assert kwargs["commit"] is True


class TestGetClientSubscriptionRoute:
    def test_unauthorized(self, client):
        res = client.get("/payments/subscription")

        assert res.status_code == 401

    def test_success_with_contract(self, auth_client):
        with patch(
            f"{ROUTE}.get_active_client_subscription_contract",
            return_value=FAKE_FORMATTED_CONTRACT,
        ):
            res = auth_client.get("/payments/subscription")

        assert res.status_code == 200
        assert res.get_json()["contract"]["contract_id"] == 1

    def test_success_with_no_contract(self, auth_client):
        with patch(
            f"{ROUTE}.get_active_client_subscription_contract",
            return_value=None,
        ):
            res = auth_client.get("/payments/subscription")

        assert res.status_code == 200
        assert res.get_json()["contract"] is None

    def test_service_error(self, auth_client):
        with patch(
            f"{ROUTE}.get_active_client_subscription_contract",
            side_effect=Exception("DB error"),
        ):
            res = auth_client.get("/payments/subscription")

        assert res.status_code == 500
        assert res.get_json()["error"] == "DB error"


class TestStartClientSubscriptionRoute:
    def test_unauthorized(self, client):
        res = client.patch("/payments/subscription/start")

        assert res.status_code == 401

    def test_success(self, auth_client):
        with patch(
            f"{ROUTE}.start_client_subscription",
            return_value=FAKE_FORMATTED_RECURRING_CONTRACT,
        ):
            res = auth_client.patch("/payments/subscription/start")

        assert res.status_code == 200
        assert res.get_json()["message"] == "Monthly subscription started successfully"
        assert res.get_json()["contract"]["is_recurring"] == 1

    def test_value_error_returns_400(self, auth_client):
        with patch(
            f"{ROUTE}.start_client_subscription",
            side_effect=ValueError("Please add a default payment method"),
        ):
            res = auth_client.patch("/payments/subscription/start")

        assert res.status_code == 400
        assert res.get_json()["error"] == "Please add a default payment method"

    def test_service_error_returns_500(self, auth_client):
        with patch(
            f"{ROUTE}.start_client_subscription",
            side_effect=Exception("DB error"),
        ):
            res = auth_client.patch("/payments/subscription/start")

        assert res.status_code == 500
        assert res.get_json()["error"] == "DB error"


class TestCancelClientSubscriptionRoute:
    def test_unauthorized(self, client):
        res = client.patch("/payments/subscription/cancel")

        assert res.status_code == 401

    def test_success(self, auth_client):
        cancelled_contract = {
            **FAKE_FORMATTED_RECURRING_CONTRACT,
            "is_recurring": 0,
            "next_billing_date": None,
        }

        with patch(
            f"{ROUTE}.cancel_client_subscription",
            return_value=cancelled_contract,
        ):
            res = auth_client.patch("/payments/subscription/cancel")

        assert res.status_code == 200
        assert (
            res.get_json()["message"] == "Monthly subscription cancelled successfully"
        )
        assert res.get_json()["contract"]["is_recurring"] == 0

    def test_value_error_returns_400(self, auth_client):
        with patch(
            f"{ROUTE}.cancel_client_subscription",
            side_effect=ValueError("You do not have an active coach contract"),
        ):
            res = auth_client.patch("/payments/subscription/cancel")

        assert res.status_code == 400
        assert res.get_json()["error"] == "You do not have an active coach contract"

    def test_service_error_returns_500(self, auth_client):
        with patch(
            f"{ROUTE}.cancel_client_subscription",
            side_effect=Exception("DB error"),
        ):
            res = auth_client.patch("/payments/subscription/cancel")

        assert res.status_code == 500
        assert res.get_json()["error"] == "DB error"
