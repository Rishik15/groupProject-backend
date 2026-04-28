# Routes: /dashboard/coach — getContracts.py, getRevenue.py, clientGrowth.py, getMetrics.py
# Services: app/services/dashboard/coach — getCoachContracts.py, getRevenueMonth.py, getClientGrowth.py, getMetrics.py

from unittest.mock import patch

CONTRACTS_SVC = "app.services.dashboard.coach.getCoachContracts"
REVENUE_SVC = "app.services.dashboard.coach.getRevenueMonth"
GROWTH_SVC = "app.services.dashboard.coach.getClientGrowth"
METRICS_SVC = "app.services.dashboard.coach.getMetrics"

CONTRACTS_ROUTE = "app.routes.dashboard.coach.getContracts"
REVENUE_ROUTE = "app.routes.dashboard.coach.getRevenue"
GROWTH_ROUTE = "app.routes.dashboard.coach.clientGrowth"
METRICS_ROUTE = "app.routes.dashboard.coach.getMetrics"

FAKE_CONTRACT_ROW = {
    "contract_id": 1, "user_id": 2, "first_name": "Alex", "last_name": "Smith",
    "start_date": "2024-06-01", "end_date": None,
    "active": 1, "agreed_price": 75.0, "contract_text": "Coaching agreement",
}

PENDING_ROW = {**FAKE_CONTRACT_ROW, "active": 0, "end_date": None}
HISTORY_ROW = {**FAKE_CONTRACT_ROW, "active": 0, "end_date": "2024-07-01"}


class TestGetCoachContracts:
    def test_categorizesPresent(self):
        from app.services.dashboard.coach.getCoachContracts import getCoachContracts
        with patch(f"{CONTRACTS_SVC}.run_query", return_value=[FAKE_CONTRACT_ROW]):
            result = getCoachContracts(coach_id=3)
        assert len(result["present"]) == 1
        assert result["present"][0]["name"] == "Alex Smith"

    def test_categorizesPending(self):
        from app.services.dashboard.coach.getCoachContracts import getCoachContracts
        with patch(f"{CONTRACTS_SVC}.run_query", return_value=[PENDING_ROW]):
            result = getCoachContracts(coach_id=3)
        assert len(result["pending"]) == 1

    def test_categorizesHistory(self):
        from app.services.dashboard.coach.getCoachContracts import getCoachContracts
        with patch(f"{CONTRACTS_SVC}.run_query", return_value=[HISTORY_ROW]):
            result = getCoachContracts(coach_id=3)
        assert len(result["history"]) == 1

    def test_returnsEmptyCategories(self):
        from app.services.dashboard.coach.getCoachContracts import getCoachContracts
        with patch(f"{CONTRACTS_SVC}.run_query", return_value=[]):
            result = getCoachContracts(coach_id=3)
        assert result == {"pending": [], "present": [], "history": []}


class TestGetRevenueLast6Months:
    def test_returnsRevenue(self):
        from app.services.dashboard.coach.getRevenueMonth import getRevenueLast6Months
        rows = [{"month": "Jun", "month_num": 6, "revenue": 150.0}]
        with patch(f"{REVENUE_SVC}.run_query", return_value=rows):
            result = getRevenueLast6Months(coach_id=3)
        assert len(result) == 1
        assert result[0]["month"] == "Jun"

    def test_returnsEmptyList(self):
        from app.services.dashboard.coach.getRevenueMonth import getRevenueLast6Months
        with patch(f"{REVENUE_SVC}.run_query", return_value=[]):
            result = getRevenueLast6Months(coach_id=3)
        assert result == []


class TestGetClientGrowthLast3Months:
    def test_returnsGrowth(self):
        from app.services.dashboard.coach.getClientGrowth import getClientGrowthLast3Months
        rows = [{"month": "Jun", "month_num": 6, "new_clients": 3}]
        with patch(f"{GROWTH_SVC}.run_query", return_value=rows):
            result = getClientGrowthLast3Months(coach_id=3)
        assert len(result) == 1
        assert result[0]["new_clients"] == 3

    def test_returnsEmptyList(self):
        from app.services.dashboard.coach.getClientGrowth import getClientGrowthLast3Months
        with patch(f"{GROWTH_SVC}.run_query", return_value=[]):
            result = getClientGrowthLast3Months(coach_id=3)
        assert result == []


class TestGetCoachMetrics:
    def test_returnsMetrics(self):
        from app.services.dashboard.coach.getMetrics import get_coach_metrics
        with patch(f"{METRICS_SVC}.run_query", side_effect=[
            [{"count": 5}],
            [{"count": 3}],
            [{"revenue": 375.0}],
            [{"revenue": 225.0}],
            [{"count": 2}],
            [{"count": 8}],
            [{"avg_rating": 4.5, "total_reviews": 10}],
        ]):
            result = get_coach_metrics(coach_id=3)
        assert result["activeClients"]["count"] == 5
        assert result["activeClients"]["diff"] == 2
        assert result["revenue"]["amount"] == 375.0
        assert result["sessions"]["week"] == 2
        assert result["rating"]["avg"] == 4.5

    def test_returnsZeroMetrics(self):
        from app.services.dashboard.coach.getMetrics import get_coach_metrics
        with patch(f"{METRICS_SVC}.run_query", side_effect=[
            [{"count": 0}],
            [{"count": 0}],
            [{"revenue": 0}],
            [{"revenue": 0}],
            [{"count": 0}],
            [{"count": 0}],
            [{"avg_rating": 0, "total_reviews": 0}],
        ]):
            result = get_coach_metrics(coach_id=3)
        assert result["activeClients"]["count"] == 0
        assert result["revenue"]["amount"] == 0.0
        assert result["rating"]["avg"] == 0.0


class TestGetContractsRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/coach/contracts")
        assert res.status_code == 401

    def test_userNotFound(self, coach_client):
        with patch(f"{CONTRACTS_ROUTE}.checkUserExists", return_value=False):
            res = coach_client.get("/dashboard/coach/contracts")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{CONTRACTS_ROUTE}.checkUserExists", return_value=True):
            with patch(f"{CONTRACTS_ROUTE}.getCoachContracts", return_value={
                "pending": [], "present": [], "history": []
            }):
                res = coach_client.get("/dashboard/coach/contracts")
        assert res.status_code == 200
        data = res.get_json()
        assert "pending_requests" in data
        assert "present_contracts" in data
        assert "history_contracts" in data


class TestGetRevenueRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/coach/revenue")
        assert res.status_code == 401

    def test_userNotFound(self, coach_client):
        with patch(f"{REVENUE_ROUTE}.checkUserExists", return_value=False):
            res = coach_client.get("/dashboard/coach/revenue")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{REVENUE_ROUTE}.checkUserExists", return_value=True):
            with patch(f"{REVENUE_ROUTE}.getRevenueLast6Months", return_value=[]):
                res = coach_client.get("/dashboard/coach/revenue")
        assert res.status_code == 200
        assert "revenue" in res.get_json()


class TestClientGrowthRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/coach/clientGrowth")
        assert res.status_code == 401

    def test_userNotFound(self, coach_client):
        with patch(f"{GROWTH_ROUTE}.checkUserExists", return_value=False):
            res = coach_client.get("/dashboard/coach/clientGrowth")
        assert res.status_code == 401

    def test_success(self, coach_client):
        with patch(f"{GROWTH_ROUTE}.checkUserExists", return_value=True):
            with patch(f"{GROWTH_ROUTE}.getClientGrowthLast3Months", return_value=[]):
                res = coach_client.get("/dashboard/coach/clientGrowth")
        assert res.status_code == 200
        data = res.get_json()
        assert "client_growth" in data
        assert data["count"] == 0


class TestGetCoachMetricsRoute:
    def test_unauthorized(self, client):
        res = client.get("/dashboard/coach/metric")
        assert res.status_code == 401

    def test_success(self, coach_client):
        fake_metrics = {
            "activeClients": {"count": 5, "diff": 2},
            "revenue": {"amount": 375.0, "diff": 150.0},
            "sessions": {"week": 2, "month": 8},
            "rating": {"avg": 4.5, "count": 10},
        }
        with patch(f"{METRICS_ROUTE}.get_coach_metrics", return_value=fake_metrics):
            res = coach_client.get("/dashboard/coach/metric")
        assert res.status_code == 200
        assert res.get_json()["activeClients"]["count"] == 5