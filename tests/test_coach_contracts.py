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
    "contract_text": "Coaching agreement",
    "active": 0,
    "created_at": "2024-05-01",
    "updated_at": "2024-05-01",
}

ACTIVE_CONTRACT = {**FAKE_CONTRACT, "active": 1}


class TestGetCoachContractsService:
    def test_returnsContracts(self):
        from app.services.contracts.coachContractActions import getCoachContractsService
        with patch(f"{SVC}.run_query", return_value=[FAKE_CONTRACT]):
            result = getCoachContractsService(coach_id=3)
        assert len(result) == 1
        assert result[0]["contract_id"] == 1

    def test_returnsEmptyList(self):
        from app.services.contracts.coachContractActions import getCoachContractsService
        with patch(f"{SVC}.run_query", return_value=[]):
            result = getCoachContractsService(coach_id=3)
        assert result == []


class TestGetUsersPerContract:
    def test_returnsUserName(self):
        from app.services.contracts.coachContractActions import getUsersPerContract
        with patch(f"{SVC}.run_query", return_value=[{"first_name": "Alex", "last_name": "Smith"}]):
            result = getUsersPerContract(user_id=2)
        assert result[0]["first_name"] == "Alex"

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
        from app.services.contracts.coachContractActions import getCoachContractsByStatusService
        with patch(f"{SVC}.run_query", return_value=[ACTIVE_CONTRACT]):
            result = getCoachContractsByStatusService(coach_id=3, active=1)
        assert len(result) == 1
        assert result[0]["active"] == 1

    def test_returnsEmptyList(self):
        from app.services.contracts.coachContractActions import getCoachContractsByStatusService
        with patch(f"{SVC}.run_query", return_value=[]):
            result = getCoachContractsByStatusService(coach_id=3, active=1)
        assert result == []


class TestGetSingleCoachContractService:
    def test_returnsContract(self):
        from app.services.contracts.coachContractActions import getSingleCoachContractService
        with patch(f"{SVC}.run_query", return_value=[FAKE_CONTRACT]):
            result = getSingleCoachContractService(coach_id=3, contract_id=1)
        assert result["contract_id"] == 1

    def test_returnsNoneWhenNotFound(self):
        from app.services.contracts.coachContractActions import getSingleCoachContractService
        with patch(f"{SVC}.run_query", return_value=[]):
            result = getSingleCoachContractService(coach_id=3, contract_id=999)
        assert result is None


class TestCoachRejectsContractService:
    def test_success(self):
        from app.services.contracts.coachContractActions import coachRejectsContractService
        with patch(f"{SVC}.run_query", return_value=None):
            coachRejectsContractService(contract_id=1)


class TestCoachTerminatesContractService:
    def test_success(self):
        from app.services.contracts.coachContractActions import coachTerminatesContractService
        with patch(f"{SVC}.run_query", return_value=None):
            coachTerminatesContractService(contract_id=1)


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
        with patch(f"{ROUTE}.cca.getCoachContractsService", return_value=[dict(FAKE_CONTRACT)]):
            with patch(f"{ROUTE}.cca.getUsersPerContract", return_value=[{"first_name": "Alex", "last_name": "Smith"}]):
                res = coach_client.get("/contract/getAllCoachSideContracts")
        assert res.status_code == 200
        data = res.get_json()["Response"]
        assert data[0]["first_name"] == "Alex"

    def test_successWithMissingUser(self, coach_client):
        with patch(f"{ROUTE}.cca.getCoachContractsService", return_value=[dict(FAKE_CONTRACT)]):
            with patch(f"{ROUTE}.cca.getUsersPerContract", return_value=[]):
                res = coach_client.get("/contract/getAllCoachSideContracts")
        assert res.status_code == 200
        data = res.get_json()["Response"]
        assert data[0]["first_name"] is None


class TestGetCoachActiveContractsRoute:
    def test_unauthorized(self, client):
        res = client.get("/contract/getCoachActiveContracts")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.cca.getCoachContractsByStatusService", return_value=[ACTIVE_CONTRACT]):
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
        with patch(f"{ROUTE}.cca.getCoachContractsByStatusService", return_value=[FAKE_CONTRACT]):
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
            res = coach_client.patch("/contract/coachAcceptContract", json={"contract_id": 999})
        assert res.status_code == 404

    def test_contractAlreadyActive(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=ACTIVE_CONTRACT):
            res = coach_client.patch("/contract/coachAcceptContract", json={"contract_id": 1})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=FAKE_CONTRACT):
            with patch(f"{ROUTE}.cca.getUserGivenContract", return_value=[{"user_id": 2}]):
                with patch(f"{ROUTE}.cca.coachAcceptsContractService", return_value=None):
                    res = coach_client.patch("/contract/coachAcceptContract", json={"contract_id": 1})
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
            res = coach_client.patch("/contract/coachRejectContract", json={"contract_id": 999})
        assert res.status_code == 404

    def test_contractAlreadyActive(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=ACTIVE_CONTRACT):
            res = coach_client.patch("/contract/coachRejectContract", json={"contract_id": 1})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=FAKE_CONTRACT):
            with patch(f"{ROUTE}.cca.coachRejectsContractService", return_value=None):
                res = coach_client.patch("/contract/coachRejectContract", json={"contract_id": 1})
        assert res.status_code == 200


class TestCoachTerminateContractRoute:
    def test_unauthorized(self, client):
        res = client.patch("/contract/coachTerminateContract", json={"contract_id": 1})
        assert res.status_code == 401

    def test_missingContractId(self, coach_client):
        res = coach_client.patch("/contract/coachTerminateContract", json={})
        assert res.status_code == 400

    def test_contractNotFound(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=None):
            res = coach_client.patch("/contract/coachTerminateContract", json={"contract_id": 999})
        assert res.status_code == 404

    def test_contractAlreadyInactive(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=FAKE_CONTRACT):
            res = coach_client.patch("/contract/coachTerminateContract", json={"contract_id": 1})
        assert res.status_code == 400

    def test_success(self, coach_client):
        with patch(f"{ROUTE}.cca.getSingleCoachContractService", return_value=ACTIVE_CONTRACT):
            with patch(f"{ROUTE}.cca.coachTerminatesContractService", return_value=None):
                res = coach_client.patch("/contract/coachTerminateContract", json={"contract_id": 1})
        assert res.status_code == 200