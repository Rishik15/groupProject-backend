from flask import current_app, jsonify, redirect, request, session
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport.requests import Request

from . import auth_bp
from app.services.auth.googleLoginService import resolve_or_create_google_user


def build_google_login_flow(state: str | None = None):
    client_secrets_file = current_app.config["GOOGLE_OAUTH_CLIENT_SECRETS_FILE"]
    redirect_uri = current_app.config["GOOGLE_LOGIN_REDIRECT_URI"]
    scopes = current_app.config["GOOGLE_LOGIN_SCOPES"]

    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


def _coerce_email_verified(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() == "true"

    return bool(value)


@auth_bp.route("/googleLogin/start", methods=["GET"])
def google_login_start():
    flow = build_google_login_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )

    session["google_login_state"] = state
    session["google_login_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@auth_bp.route("/googleLogin/callback", methods=["GET"])
def google_login_callback():
    saved_state = session.get("google_login_state")
    if not saved_state:
        return jsonify({"error": "Missing OAuth state"}), 400

    flow = build_google_login_flow(state=saved_state)

    code_verifier = session.get("google_login_code_verifier")
    if not code_verifier:
        return jsonify({"error": "Missing code verifier"}), 400

    flow.code_verifier = code_verifier

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    credentials = flow.credentials

    try:
        idinfo = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            audience=credentials.client_id,
            clock_skew_in_seconds=10,
        )
    except Exception as e:
        return jsonify({"error": f"Failed to verify Google identity: {str(e)}"}), 500

    google_sub = idinfo.get("sub")
    google_email = idinfo.get("email")
    email_verified = _coerce_email_verified(idinfo.get("email_verified"))
    full_name = idinfo.get("name")

    if not google_sub or not google_email:
        return jsonify({"error": "Google account did not return required identity fields"}), 400

    user = resolve_or_create_google_user(
        google_sub=google_sub,
        google_email=google_email,
        email_verified=email_verified,
        full_name=full_name,
    )

    if user is None:
        return jsonify({"error": "Failed to resolve Google user"}), 500

    session.permanent = True
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]
    session["auth_provider"] = "google"

    session.pop("google_login_state", None)
    session.pop("google_login_code_verifier", None)

    return redirect(current_app.config["GOOGLE_LOGIN_FRONTEND_REDIRECT_URI"])


@auth_bp.route("/googleLogin/status", methods=["GET"])
def google_login_status():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401

    return jsonify({
        "authenticated": True,
        "user_id": session.get("user_id"),
        "role": session.get("role"),
        "auth_provider": session.get("auth_provider", "password"),
    }), 200