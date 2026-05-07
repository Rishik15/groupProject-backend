from unittest.mock import patch

SVC = "app.services.contracts.coachContractActions"
ROUTE = "app.routes.contracts.coach_contract_actions"

FAKE_CONTRACT = {
    "contract_id": 1,
    "coach_id": 3,
    "user_id": 2,
    "agreed_price": 75.00,
    "start_date": "2024-06-01",
    "end_date": None,
    "contract_text": (
        "training_reason:Build muscle|"
        "goals:Get stronger|"
        "preferred_schedule:Monday evenings|"
        "notes:No injuries|"
        "payment_type:recurring|"
        "price:75.0|"
        "payment_note:Payment method saved for contract start."
    ),
    "active": 0,
    "is_recurring": 1,
    "created_at": "2024-05-01",
    "updated_at": "2024-05-01",
    "first_name": "Alex",
    "last_name": "Smith",
}

ACTIVE_CONTRACT = {
    **FAKE_CONTRACT,
    "active": 1,
    "end_date": None,
}

CLOSED_CONTRACT = {
    **FAKE_CONTRACT,
    "active": 0,
    "end_date": "2024-07-01",
}


class TestContractFormattingHelpers:
    def test_parse_contract_text(self):
        from app.services.contracts.coachContractActions import parse_contract_text

        result = parse_contract_text(FAKE_CONTRACT["contract_text"])

        assert result["training_reason"] == "Build muscle"
        assert result["goals"] == "Get stronger"
        assert result["preferred_schedule"] == "Monday evenings"
        assert result["notes"] == "No injuries"
        assert result["payment_type"] == "recurring"
        assert result["price"] == "75.0"

    def test_parse_contract_text_empty(self):
        from app.services.contracts.coachContractActions import parse_contract_text

        result = parse_contract_text(None)

        assert result["training_reason"] == ""
        assert result["goals"] == ""
        assert result["preferred_schedule"] == ""
        assert result["notes"] == ""

    def test_get_contract_status_label_pending(self):
        from app.services.contracts.coachContractActions import (
            get_contract_status_label,
        )

        assert get_contract_status_label(FAKE_CONTRACT) == "pending"

    def test_get_contract_status_label_active(self):
        from app.services.contracts.coachContractActions import (
            get_contract_status_label,
        )

        assert get_contract_status_label(ACTIVE_CONTRACT) == "active"

    def test_get_contract_status_label_closed(self):
        from app.services.contracts.coachContractActions import (
            get_contract_status_label,
        )

        assert get_contract_status_label(CLOSED_CONTRACT) == "closed"

    def test_format_contract(self):
        from app.services.contracts.coachContractActions import format_contract

        result = format_contract(dict(FAKE_CONTRACT))

        assert result["contract_id"] == 1
        assert result["first_name"] == "Alex"
        assert result["last_name"] == "Smith"
        assert result["status"] == "pending"
        assert result["request_details"]["training_reason"] == "Build muscle"
        assert result["start_date"] == "2024-06-01"
        assert result["end_date"] is None
        assert result["created_at"] == "2024-05-01T00:00:00"
        assert result["updated_at"] == "2024-05-01T00:00:00"


class TestGetCoachContractsService:
    def test_returnsContracts(self):
        from app.services.contracts.coachContractActions import getCoachContractsService

        with patch(f"{SVC}.run_query", return_value=[dict(FAKE_CONTRACT)]):
            result = getCoachContractsService(coach_id=3)

        assert len(result) == 1
        assert result[0]["contract_id"] == 1
        assert result[0]["first_name"] == "Alex"
        assert result[0]["last_name"] == "Smith"
        assert result[0]["status"] == "pending"
        assert result[0]["request_details"]["goals"] == "Get stronger"

    def test_returnsEmptyList(self):
        from app.services.contracts.coachContractActions import getCoachContractsService

        with patch(f"{SVC}.run_query", return_value=[]):
            result = getCoachContractsService(coach_id=3)

        assert result == []


class TestGetUsersPerContract:
    def test_returnsUserName(self):
        from app.services.contracts.coachContractActions import getUsersPerContract

        with patch(
            f"{SVC}.run_query",
            return_value=[{"first_name": "Alex", "last_name": "Smith"}],
        ):
            result = getUsersPerContract(user_id=2)

        assert result[0]["first_name"] == "Alex"
        assert result[0]["last_name"] == "Smith"

    def test_returnsEmptyWhenNotFound(self):
        from app.services.contracts.coachContractActions import getUsersPerContract

        with patch(f"{SVC}.run_query", return_value=[]):
            result = getUsersPerContract(user_id=999)

        assert result == []


class TestGetUserGivenContract:
    def test_returnsUserId(self):
        from app.services.contracts.coachContractActions import getUserGivenContract

        with patch(f"{SVC}.run_query", return_value=[{"user_id": 2}]):
            result = getUserGivenContract(contract_id=1)

        assert result[0]["user_id"] == 2

    def test_returnsEmptyWhenNotFound(self):
        from app.services.contracts.coachContractActions import getUserGivenContract

        with patch(f"{SVC}.run_query", return_value=[]):
            result = getUserGivenContract(contract_id=999)

        assert result == []


class TestGetCoachContractsByStatusService:
    def test_returnsActiveContracts(self):
        from app.services.contracts.coachContractActions import (
            getCoachContractsByStatusService,
        )

        with patch(f"{SVC}.run_query", return_value=[dict(ACTIVE_CONTRACT)]):
            result = getCoachContractsByStatusService(coach_id=3, active=1)

        assert len(result) == 1
        assert result[0]["active"] == 1
        assert result[0]["status"] == "active"
        assert result[0]["first_name"] == "Alex"

    def test_returnsEmptyList(self):
        from app.services.contracts.coachContractActions import (
            getCoachContractsByStatusService,
        )

        with patch(f"{SVC}.run_query", return_value=[]):
            result = getCoachContractsByStatusService(coach_id=3, active=1)

        assert result == []


class TestGetSingleCoachContractService:
    def test_returnsContract(self):
        from app.services.contracts.coachContractActions import (
            getSingleCoachContractService,
        )

        with patch(f"{SVC}.run_query", return_value=[dict(FAKE_CONTRACT)]):
            result = getSingleCoachContractService(coach_id=3, contract_id=1)

        assert result["contract_id"] == 1
        assert result["status"] == "pending"
        assert result["first_name"] == "Alex"
        assert result["request_details"]["training_reason"] == "Build muscle"

    def test_returnsNoneWhenNotFound(self):
        from app.services.contracts.coachContractActions import (
            getSingleCoachContractService,
        )

        with patch(f"{SVC}.run_query", return_value=[]):
            result = getSingleCoachContractService(coach_id=3, contract_id=999)

        assert result is None


class TestCoachAcceptsContractService:
    def test_success(self):
        from app.services.contracts.coachContractActions import (
            coachAcceptsContractService,
        )

        with patch(f"{SVC}.run_query", side_effect=[[{"is_recurring": 1}], None]):
            with patch(f"{SVC}.buildDefaultConversation", return_value=10):
                coachAcceptsContractService(
                    contract_id=1,
                    coach_id=3,
                    user_id=2,
                    user_timezone="America/New_York",
                )

    def test_contract_not_found_raises(self):
        from app.services.contracts.coachContractActions import (
            coachAcceptsContractService,
        )

        with patch(f"{SVC}.run_query", return_value=[]):
            try:
                coachAcceptsContractService(
                    contract_id=999,
                    coach_id=3,
                    user_id=2,
                    user_timezone="America/New_York",
                )
                assert False
            except Exception as error:
                assert str(error) == "Contract not found"


class TestCoachRejectsContractService:
    def test_success(self):
        from app.services.contracts.coachContractActions import (
            coachRejectsContractService,
        )

        with patch(f"{SVC}.run_query", return_value=None):
            coachRejectsContractService(
                contract_id=1,
                user_timezone="America/New_York",
            )


class TestCoachTerminatesContractService:
    def test_success(self):
        from app.services.contracts.coachContractActions import (
            coachTerminatesContractService,
        )

        with patch(f"{SVC}.run_query", return_value=None):
            coachTerminatesContractService(
                contract_id=1,
                user_timezone="America/New_York",
            )


class TestGetAllCoachSideContractsRoute:
    def test_unauthorized(self, client):
        res = client.get("/contract/getAllCoachSideContracts")

        assert res.status_code == 401

    def test_successNoContracts(self, coach_client):
        with patch(f"{ROUTE}.cca.getCoachContractsService", return_value=[]):
            res = coach_client.get("/contract/getAllCoachSideContracts")

        assert res.status_code == 200
        assert res.get_json()["Response"] == []

    def test_successWithContracts(self, coach_client):
        formatted_contract = {
            **dict(FAKE_CONTRACT),
            "status": "pending",
            "request_details": {
                "training_reason": "Build muscle",
                "goals": "Get stronger",
                "preferred_schedule": "Monday evenings",
                "notes": "No injuries",
                "payment_type": "recurring",
                "price": "75.0",
                "payment_note": "Payment method saved for contract start.",
            },
        }

        with patch(
            f"{ROUTE}.cca.getCoachContractsService",
            return_value=[formatted_contract],
        ):
            res = coach_client.get("/contract/getAllCoachSideContracts")

        assert res.status_code == 200

        data = res.get_json()["Response"]

        assert len(data) == 1
        assert data[0]["contract_id"] == 1
        assert data[0]["first_name"] == "Alex"
        assert data[0]["last_name"] == "Smith"
        assert data[0]["status"] == "pending"
        assert data[0]["request_details"]["goals"] == "Get stronger"


class TestGetCoachActiveContractsRoute:
    def test_unauthorized(self, client):
        res = client.get("/contract/getCoachActiveContracts")

        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getCoachContractsByStatusService",
            return_value=[dict(ACTIVE_CONTRACT)],
        ):
            res = coach_client.get("/contract/getCoachActiveContracts")

        assert res.status_code == 200
        assert len(res.get_json()["Response"]) == 1

    def test_successEmpty(self, coach_client):
        with patch(f"{ROUTE}.cca.getCoachContractsByStatusService", return_value=[]):
            res = coach_client.get("/contract/getCoachActiveContracts")

        assert res.status_code == 200
        assert res.get_json()["Response"] == []


class TestGetCoachInactiveContractsRoute:
    def test_unauthorized(self, client):
        res = client.get("/contract/getCoachInactiveContracts")

        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getCoachContractsByStatusService",
            return_value=[dict(FAKE_CONTRACT)],
        ):
            res = coach_client.get("/contract/getCoachInactiveContracts")

        assert res.status_code == 200


class TestCoachAcceptContractRoute:
    def test_unauthorized(self, client):
        res = client.patch("/contract/coachAcceptContract", json={"contract_id": 1})

        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.patch("/contract/coachAcceptContract", json={})

        assert res.status_code == 400

    def test_contractNotFound(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=None):
            res = coach_client.patch(
                "/contract/coachAcceptContract",
                json={"contract_id": 999},
            )

        assert res.status_code == 404

    def test_contractAlreadyActive(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(ACTIVE_CONTRACT),
        ):
            res = coach_client.patch(
                "/contract/coachAcceptContract",
                json={"contract_id": 1},
            )

        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(FAKE_CONTRACT),
        ):
            with patch(
                f"{ROUTE}.cca.getUserGivenContract", return_value=[{"user_id": 2}]
            ):
                with patch(
                    f"{ROUTE}.cca.coachAcceptsContractService",
                    return_value=None,
                ):
                    res = coach_client.patch(
                        "/contract/coachAcceptContract",
                        json={"contract_id": 1},
                    )

        assert res.status_code == 200


class TestCoachRejectContractRoute:
    def test_unauthorized(self, client):
        res = client.patch("/contract/coachRejectContract", json={"contract_id": 1})

        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.patch("/contract/coachRejectContract", json={})

        assert res.status_code == 400

    def test_contractNotFound(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=None):
            res = coach_client.patch(
                "/contract/coachRejectContract",
                json={"contract_id": 999},
            )

        assert res.status_code == 404

    def test_contractAlreadyActive(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(ACTIVE_CONTRACT),
        ):
            res = coach_client.patch(
                "/contract/coachRejectContract",
                json={"contract_id": 1},
            )

        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(FAKE_CONTRACT),
        ):
            with patch(f"{ROUTE}.cca.coachRejectsContractService", return_value=None):
                res = coach_client.patch(
                    "/contract/coachRejectContract",
                    json={"contract_id": 1},
                )

        assert res.status_code == 200


class TestCoachTerminateContractRoute:
    def test_unauthorized(self, client):
        res = client.patch(
            "/contract/coachTerminateContract",
            json={"contract_id": 1},
        )

        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.patch("/contract/coachTerminateContract", json={})

        assert res.status_code == 400

    def test_contractNotFound(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=None):
            res = coach_client.patch(
                "/contract/coachTerminateContract",
                json={"contract_id": 999},
            )

        assert res.status_code == 404

    def test_contractAlreadyInactive(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(FAKE_CONTRACT),
        ):
            res = coach_client.patch(
                "/contract/coachTerminateContract",
                json={"contract_id": 1},
            )

        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(
            f"{ROUTE}.cca.getSingleCoachContractService",
            return_value=dict(ACTIVE_CONTRACT),
        ):
            with patch(
                f"{ROUTE}.cca.coachTerminatesContractService", return_value=None
            ):
                res = coach_client.patch(
                    "/contract/coachTerminateContract",
                    json={"contract_id": 1},
                )

        assert res.status_code == 200
