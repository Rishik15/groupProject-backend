from unittest.mock import patch

LOGIN = "app.routes.auth.login"
REGISTER = "app.routes.auth.register"
LOGOUT = "app.routes.auth.logout"
ME = "app.routes.auth.me"

FAKE_USER_INFO = {
    "first_name": "Alex",
    "last_name": "Smith",
    "email": "alex@example.com",
    "profile_picture": None,
}

FAKE_ROLES = ["client"]
FAKE_COACH_APP_STATUS = None


class TestLoginRoute:
    def test_invalidCredentialsNoUser(self, client):
        with patch(f"{LOGIN}.getUserCreds", return_value=None):
            res = client.post("/auth/login", json={
                "email": "notfound@example.com",
                "password": "wrongpass"
            })
        assert res.status_code == 401

    def test_invalidCredentialsBadPassword(self, client):
        fake_user = {"user_id": 2, "password_hash": "hashed", "role": "client"}
        with patch(f"{LOGIN}.getUserCreds", return_value=fake_user):
            with patch(f"{LOGIN}.bcrypt.check_password_hash", return_value=False):
                res = client.post("/auth/login", json={
                    "email": "alex@example.com",
                    "password": "wrongpass"
                })
        assert res.status_code == 401

    def test_success(self, client):
        fake_user = {"user_id": 2, "password_hash": "hashed", "role": "client"}
        with patch(f"{LOGIN}.getUserCreds", return_value=fake_user):
            with patch(f"{LOGIN}.bcrypt.check_password_hash", return_value=True):
                with patch(f"{LOGIN}.getUserRoles", return_value=FAKE_ROLES):
                    with patch(f"{LOGIN}.getUserInfo", return_value=FAKE_USER_INFO):
                        with patch(f"{LOGIN}.getCoachApplicationStatus", return_value=None):
                            res = client.post("/auth/login", json={
                                "email": "alex@example.com",
                                "password": "Rishik@1"
                            })
        assert res.status_code == 200
        assert res.get_json()["success"] is True


class TestRegisterRoute:
    def test_invalidRole(self, client):
        res = client.post("/auth/register", json={
            "email": "new@example.com",
            "password": "Pass@123",
            "name": "New User",
            "role": "superadmin"
        })
        assert res.status_code == 400

    def test_userAlreadyExists(self, client):
        with patch(f"{REGISTER}.checkUserExists", return_value=True):
            res = client.post("/auth/register", json={
                "email": "alex@example.com",
                "password": "Pass@123",
                "name": "Alex Smith",
                "role": "client"
            })
        assert res.status_code == 409

    def test_successSingleName(self, client):
        with patch(f"{REGISTER}.checkUserExists", return_value=False):
            with patch(f"{REGISTER}.bcrypt.generate_password_hash", return_value=b"hashed"):
                with patch(f"{REGISTER}.addClient", return_value=10):
                    with patch(f"{REGISTER}.getUserRoles", return_value=FAKE_ROLES):
                        with patch(f"{REGISTER}.getUserInfo", return_value=FAKE_USER_INFO):
                            with patch(f"{REGISTER}.getCoachApplicationStatus", return_value=None):
                                res = client.post("/auth/register", json={
                                    "email": "new@example.com",
                                    "password": "Pass@123",
                                    "name": "Alex",
                                    "role": "client"
                                })
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_successFullName(self, client):
        with patch(f"{REGISTER}.checkUserExists", return_value=False):
            with patch(f"{REGISTER}.bcrypt.generate_password_hash", return_value=b"hashed"):
                with patch(f"{REGISTER}.addClient", return_value=10):
                    with patch(f"{REGISTER}.getUserRoles", return_value=FAKE_ROLES):
                        with patch(f"{REGISTER}.getUserInfo", return_value=FAKE_USER_INFO):
                            with patch(f"{REGISTER}.getCoachApplicationStatus", return_value=None):
                                res = client.post("/auth/register", json={
                                    "email": "new@example.com",
                                    "password": "Pass@123",
                                    "name": "Alex Smith",
                                    "role": "client"
                                })
        assert res.status_code == 200

    def test_successCoachRole(self, client):
        with patch(f"{REGISTER}.checkUserExists", return_value=False):
            with patch(f"{REGISTER}.bcrypt.generate_password_hash", return_value=b"hashed"):
                with patch(f"{REGISTER}.addClient", return_value=10):
                    with patch(f"{REGISTER}.getUserRoles", return_value=["coach"]):
                        with patch(f"{REGISTER}.getUserInfo", return_value=FAKE_USER_INFO):
                            with patch(f"{REGISTER}.getCoachApplicationStatus", return_value=None):
                                res = client.post("/auth/register", json={
                                    "email": "coach@example.com",
                                    "password": "Pass@123",
                                    "name": "Sam Coach",
                                    "role": "coach"
                                })
        assert res.status_code == 200


class TestUpdateRoleRoute:
    def test_unauthorized(self, client):
        res = client.post("/auth/updateRole", json={"role": "client"})
        assert res.status_code == 401

    def test_invalidRole(self, auth_client):
        res = auth_client.post("/auth/updateRole", json={"role": "admin"})
        assert res.status_code == 400

    def test_success(self, auth_client):
        with patch(f"{REGISTER}.initialize_client_role", return_value=None):
            with patch(f"{REGISTER}.getUserInfo", return_value=FAKE_USER_INFO):
                with patch(f"{REGISTER}.getUserRoles", return_value=FAKE_ROLES):
                    with patch(f"{REGISTER}.getCoachApplicationStatus", return_value=None):
                        with patch(f"{REGISTER}.getUserOnboardingStatus", return_value=False):
                            res = auth_client.post("/auth/updateRole", json={"role": "client"})
        assert res.status_code == 200
        assert res.get_json()["authenticated"] is True


class TestLogoutRoute:
    def test_noActiveSession(self, client):
        res = client.post("/auth/logout")
        assert res.status_code == 400

    def test_success(self, auth_client):
        res = auth_client.post("/auth/logout")
        assert res.status_code == 200
        assert res.get_json()["message"] == "Logged out successfully"


class TestMeRoute:
    def test_unauthenticated(self, client):
        res = client.get("/auth/me")
        assert res.status_code == 401
        assert res.get_json()["authenticated"] is False

    def test_userNotFound(self, auth_client):
        with patch(f"{ME}.checkUserExists", return_value=False):
            res = auth_client.get("/auth/me")
        assert res.status_code == 401

    def test_successClientRole(self, auth_client):
        with patch(f"{ME}.checkUserExists", return_value=True):
            with patch(f"{ME}.getUserRoles", return_value=["client"]):
                with patch(f"{ME}.getUserInfo", return_value=FAKE_USER_INFO):
                    with patch(f"{ME}.getCoachApplicationStatus", return_value=None):
                        with patch(f"{ME}.getCoachModeActivated", return_value=False):
                            with patch(f"{ME}.getUserOnboardingStatus", return_value=False):
                                res = auth_client.get("/auth/me")
        assert res.status_code == 200
        assert res.get_json()["authenticated"] is True

    def test_successCoachRole(self, coach_client):
        with patch(f"{ME}.checkUserExists", return_value=True):
            with patch(f"{ME}.getUserRoles", return_value=["coach"]):
                with patch(f"{ME}.getUserInfo", return_value=FAKE_USER_INFO):
                    with patch(f"{ME}.getCoachApplicationStatus", return_value=None):
                        with patch(f"{ME}.getCoachModeActivated", return_value=True):
                            with patch(f"{ME}.getUserOnboardingStatus", return_value=False):
                                res = coach_client.get("/auth/me")
        assert res.status_code == 200

    def test_successAdminRole(self, admin_client):
        with patch(f"{ME}.checkUserExists", return_value=True):
            with patch(f"{ME}.getUserRoles", return_value=["admin"]):
                with patch(f"{ME}.getUserInfo", return_value=FAKE_USER_INFO):
                    with patch(f"{ME}.getCoachApplicationStatus", return_value=None):
                        with patch(f"{ME}.getCoachModeActivated", return_value=False):
                            with patch(f"{ME}.getUserOnboardingStatus", return_value=False):
                                res = admin_client.get("/auth/me")
        assert res.status_code == 200

    def test_needsOnboarding(self, auth_client):
        with patch(f"{ME}.checkUserExists", return_value=True):
            with patch(f"{ME}.getUserRoles", return_value=["client"]):
                with patch(f"{ME}.getUserInfo", return_value=FAKE_USER_INFO):
                    with patch(f"{ME}.getCoachApplicationStatus", return_value=None):
                        with patch(f"{ME}.getCoachModeActivated", return_value=False):
                            with patch(f"{ME}.getUserOnboardingStatus", return_value=True):
                                res = auth_client.get("/auth/me")
        assert res.status_code == 200
        assert res.get_json()["needs_onboarding"] is True