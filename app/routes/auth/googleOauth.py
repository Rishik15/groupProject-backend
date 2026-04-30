from flask import current_app, jsonify, redirect, request, session
from googleapiclient.discovery import build

from . import auth_bp
from app.services.google_drive import (
    build_google_auth_flow,
    clear_google_drive_connection,
    get_effective_google_drive_connection,
    get_google_drive_connection,
    save_google_drive_connection,
)


def _get_google_email_from_credentials(credentials):
    try:
        oauth2_service = build("oauth2", "v2", credentials=credentials)
        userinfo = oauth2_service.userinfo().get().execute()
        return userinfo.get("email")
    except Exception:
        return None


@auth_bp.route("/googleOauth/start", methods=["GET"])
def google_oauth_start():
    """
Start Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    session.pop("google_login_state", None)
    session.pop("google_login_code_verifier", None)
    session.pop("google_oauth_state", None)
    session.pop("google_oauth_code_verifier", None)
    session.pop("google_oauth_personal_state", None)
    session.pop("google_oauth_personal_code_verifier", None)

    flow = build_google_auth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    session["google_oauth_state"] = state
    session["google_oauth_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)

@auth_bp.route("/googleOauth/callback", methods=["GET"])
def google_oauth_callback():
    """
Callback Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    saved_state = session.get("google_oauth_state")
    if not saved_state:
        return jsonify({"error": "Missing OAuth state"}), 400

    flow = build_google_auth_flow(state=saved_state)

    code_verifier = session.get("google_oauth_code_verifier")
    if not code_verifier:
        return jsonify({"error": "Missing code verifier"}), 400

    flow.code_verifier = code_verifier

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    credentials = flow.credentials

    google_email = _get_google_email_from_credentials(credentials)

    save_google_drive_connection(
        account_scope="global",
        owner_user_id=None,
        connected_by_user_id=int(user_id),
        google_email=google_email,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        scopes=list(credentials.scopes or []),
        root_folder_id=None,
    )

    session.pop("google_oauth_state", None)
    session.pop("google_oauth_code_verifier", None)

    return redirect(current_app.config["GOOGLE_LOGIN_FRONTEND_REDIRECT_URI"])


@auth_bp.route("/googleOauth/status", methods=["GET"])
def google_oauth_status():
    """
Status Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401

    connection = get_google_drive_connection(account_scope="global", owner_user_id=None)

    if connection is None:
        return jsonify({
            "connected": False,
            "mode": "global",
            "google_email": None,
            "connected_by_user_id": None,
        }), 200

    return jsonify({
        "connected": True,
        "mode": "global",
        "google_email": connection.get("google_email"),
        "connected_by_user_id": connection.get("connected_by_user_id"),
    }), 200


@auth_bp.route("/googleOauth/disconnect", methods=["POST"])
def google_oauth_disconnect():
    """
Disconnect Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    clear_google_drive_connection(account_scope="global", owner_user_id=None)
    return jsonify({"message": "Google Drive disconnected"}), 200


@auth_bp.route("/googleOauth/personal/start", methods=["GET"])
def google_oauth_personal_start():
    """
Personal Start Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    session.pop("google_login_state", None)
    session.pop("google_login_code_verifier", None)
    session.pop("google_oauth_state", None)
    session.pop("google_oauth_code_verifier", None)
    session.pop("google_oauth_personal_state", None)
    session.pop("google_oauth_personal_code_verifier", None)

    flow = build_google_auth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )

    session["google_oauth_personal_state"] = state
    session["google_oauth_personal_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)

@auth_bp.route("/googleOauth/personal/callback", methods=["GET"])
def google_oauth_personal_callback():
    """
Callback Personal Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    saved_state = session.get("google_oauth_personal_state")
    if not saved_state:
        return jsonify({"error": "Missing OAuth state"}), 400

    flow = build_google_auth_flow(state=saved_state)

    code_verifier = session.get("google_oauth_personal_code_verifier")
    if not code_verifier:
        return jsonify({"error": "Missing code verifier"}), 400

    flow.code_verifier = code_verifier

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    credentials = flow.credentials
    google_email = _get_google_email_from_credentials(credentials)

    save_google_drive_connection(
        account_scope="user",
        owner_user_id=int(user_id),
        connected_by_user_id=int(user_id),
        google_email=google_email,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        scopes=list(credentials.scopes or []),
        root_folder_id=None,
    )

    session.pop("google_oauth_personal_state", None)
    session.pop("google_oauth_personal_code_verifier", None)

    return redirect(current_app.config["GOOGLE_LOGIN_FRONTEND_REDIRECT_URI"])

@auth_bp.route("/googleOauth/personal/status", methods=["GET"])
def google_oauth_personal_status():
    """
Status Personal Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401

    connection = get_google_drive_connection(
        account_scope="user",
        owner_user_id=int(user_id),
    )

    if connection is None:
        return jsonify({
            "connected": False,
            "mode": "user",
            "google_email": None,
            "connected_by_user_id": None,
            "owner_user_id": int(user_id),
        }), 200

    return jsonify({
        "connected": True,
        "mode": "user",
        "google_email": connection.get("google_email"),
        "connected_by_user_id": connection.get("connected_by_user_id"),
        "owner_user_id": connection.get("owner_user_id"),
    }), 200


@auth_bp.route("/googleOauth/personal/disconnect", methods=["POST"])
def google_oauth_personal_disconnect():
    """
Disconnect Personal Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    clear_google_drive_connection(
        account_scope="user",
        owner_user_id=int(user_id),
    )
    return jsonify({"message": "Personal Google Drive disconnected"}), 200


@auth_bp.route("/googleOauth/effectiveStatus", methods=["GET"])
def google_oauth_effective_status():
    """
Effective Status Google Drive OAuth
---
tags:
  - google-oauth
responses:
  302:
    description: Redirect to Google
"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401

    connection = get_effective_google_drive_connection(int(user_id))

    if connection is None:
        return jsonify({
            "connected": False,
            "effective_mode": None,
            "google_email": None,
            "connected_by_user_id": None,
            "owner_user_id": None,
        }), 200

    return jsonify({
        "connected": True,
        "effective_mode": connection.get("account_scope"),
        "google_email": connection.get("google_email"),
        "connected_by_user_id": connection.get("connected_by_user_id"),
        "owner_user_id": connection.get("owner_user_id"),
    }), 200