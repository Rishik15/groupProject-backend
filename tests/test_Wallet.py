# Route: /wallet — app/routes/wallet/wallet.py
# Service: app/services/wallet/wallet.py

from unittest.mock import patch
from datetime import datetime

SVC = "app.services.wallet.wallet"
ROUTE = "app.routes.wallet.wallet"

FAKE_USER = {"user_id": 2, "account_status": "active"}
FAKE_WALLET_ROW = {
    "user_id": 2, "balance": 500,
    "created_at": datetime(2024, 6, 1), "updated_at": datetime(2024, 6, 1),
}
FAKE_TXN_ROW = {
    "txn_id": 1, "user_id": 2, "delta_points": 100,
    "reason": "Daily survey reward", "ref_type": "daily_survey", "ref_id": None,
    "created_at": datetime(2024, 6, 1), "updated_at": datetime(2024, 6, 1),
}


class TestGetUserRow:
    def test_returnsUser(self):
        from app.services.wallet.wallet import _get_user_row
        with patch(f"{SVC}.run_query", return_value=[FAKE_USER]):
            result = _get_user_row(user_id=2)
        assert result["account_status"] == "active"

    def test_userNotFound(self):
        from app.services.wallet.wallet import _get_user_row
        import pytest
        with patch(f"{SVC}.run_query", return_value=[]):
            with pytest.raises(ValueError, match="User not found"):
                _get_user_row(user_id=999)


class TestGetOrCreateWalletRow:
    def test_returnsExistingWallet(self):
        from app.services.wallet.wallet import _get_or_create_wallet_row
        with patch(f"{SVC}.run_query", return_value=[FAKE_WALLET_ROW]):
            result = _get_or_create_wallet_row(user_id=2)
        assert result["balance"] == 500

    def test_createsWalletWhenNotFound(self):
        from app.services.wallet.wallet import _get_or_create_wallet_row
        with patch(f"{SVC}.run_query", side_effect=[[], None, [FAKE_WALLET_ROW]]):
            result = _get_or_create_wallet_row(user_id=2)
        assert result["balance"] == 500

    def test_walletCreationFailed(self):
        from app.services.wallet.wallet import _get_or_create_wallet_row
        import pytest
        with patch(f"{SVC}.run_query", side_effect=[[], None, []]):
            with pytest.raises(ValueError, match="Wallet creation failed"):
                _get_or_create_wallet_row(user_id=2)


class TestShapeWallet:
    def test_shapesCorrectly(self):
        from app.services.wallet.wallet import _shape_wallet
        result = _shape_wallet(FAKE_WALLET_ROW)
        assert result["balance"] == 500
        assert result["user_id"] == 2
        assert "created_at" in result

    def test_noneTimestamps(self):
        from app.services.wallet.wallet import _shape_wallet
        row = {**FAKE_WALLET_ROW, "created_at": None, "updated_at": None}
        result = _shape_wallet(row)
        assert result["created_at"] is None


class TestShapeWalletTransaction:
    def test_shapesCorrectly(self):
        from app.services.wallet.wallet import _shape_wallet_transaction
        result = _shape_wallet_transaction(FAKE_TXN_ROW)
        assert result["delta_points"] == 100
        assert result["reason"] == "Daily survey reward"

    def test_noneTimestamps(self):
        from app.services.wallet.wallet import _shape_wallet_transaction
        row = {**FAKE_TXN_ROW, "created_at": None, "updated_at": None}
        result = _shape_wallet_transaction(row)
        assert result["created_at"] is None


class TestGetWallet:
    def test_inactiveUserRaises(self):
        from app.services.wallet.wallet import get_wallet
        import pytest
        with patch(f"{SVC}._get_user_row", return_value={"user_id": 2, "account_status": "inactive"}):
            with pytest.raises(ValueError, match="not active"):
                get_wallet(user_id=2)

    def test_success(self):
        from app.services.wallet.wallet import get_wallet
        with patch(f"{SVC}._get_user_row", return_value=FAKE_USER):
            with patch(f"{SVC}._get_or_create_wallet_row", return_value=FAKE_WALLET_ROW):
                result = get_wallet(user_id=2)
        assert result["balance"] == 500


class TestGetWalletTransactions:
    def test_inactiveUserRaises(self):
        from app.services.wallet.wallet import get_wallet_transactions
        import pytest
        with patch(f"{SVC}._get_user_row", return_value={"user_id": 2, "account_status": "inactive"}):
            with pytest.raises(ValueError, match="not active"):
                get_wallet_transactions(user_id=2)

    def test_returnsTransactions(self):
        from app.services.wallet.wallet import get_wallet_transactions
        with patch(f"{SVC}._get_user_row", return_value=FAKE_USER):
            with patch(f"{SVC}._get_or_create_wallet_row", return_value=FAKE_WALLET_ROW):
                with patch(f"{SVC}.run_query", return_value=[FAKE_TXN_ROW]):
                    result = get_wallet_transactions(user_id=2)
        assert len(result) == 1
        assert result[0]["reason"] == "Daily survey reward"

    def test_returnsEmptyList(self):
        from app.services.wallet.wallet import get_wallet_transactions
        with patch(f"{SVC}._get_user_row", return_value=FAKE_USER):
            with patch(f"{SVC}._get_or_create_wallet_row", return_value=FAKE_WALLET_ROW):
                with patch(f"{SVC}.run_query", return_value=[]):
                    result = get_wallet_transactions(user_id=2)
        assert result == []


class TestGetWalletRoute:
    def test_unauthorized(self, client):
        res = client.get("/wallet")
        assert res.status_code == 401

    def test_valueError(self, auth_client):
        with patch(f"{ROUTE}.get_wallet", side_effect=ValueError("User account is not active")):
            res = auth_client.get("/wallet")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_wallet", return_value={"user_id": 2, "balance": 500, "created_at": None, "updated_at": None}):
            res = auth_client.get("/wallet")
        assert res.status_code == 200
        assert res.get_json()["wallet"]["balance"] == 500


class TestGetWalletTransactionsRoute:
    def test_unauthorized(self, client):
        res = client.get("/wallet/transactions")
        assert res.status_code == 401

    def test_valueError(self, auth_client):
        with patch(f"{ROUTE}.get_wallet_transactions", side_effect=ValueError("User account is not active")):
            res = auth_client.get("/wallet/transactions")
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{ROUTE}.get_wallet_transactions", return_value=[]):
            res = auth_client.get("/wallet/transactions")
        assert res.status_code == 200
        assert res.get_json()["transactions"] == []