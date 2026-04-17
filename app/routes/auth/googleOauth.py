from flask import jsonify, redirect, request, session

from . import auth_bp
from app.services.google_drive import (
    build_google_auth_flow,
    clear_google_drive_connection,
    get_google_drive_connection,
    save_google_drive_connection,
)


@auth_bp.route("/googleOauth/start", methods=["GET"])
def google_oauth_start():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    flow = build_google_auth_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    session["google_oauth_state"] = state
    session["google_oauth_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@auth_bp.route("/googleOauth/callback", methods=["GET"])
def google_oauth_callback():
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

    google_email = None

    save_google_drive_connection(
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

    return redirect("http://localhost:5173")


@auth_bp.route("/googleOauth/status", methods=["GET"])
def google_oauth_status():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401

    connection = get_google_drive_connection()

    if connection is None:
        return jsonify({
            "connected": False,
            "google_email": None,
        }), 200

    return jsonify({
        "connected": True,
        "google_email": connection.get("google_email"),
        "connected_by_user_id": connection.get("connected_by_user_id"),
    }), 200


@auth_bp.route("/googleOauth/disconnect", methods=["POST"])
def google_oauth_disconnect():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    clear_google_drive_connection()
    return jsonify({"message": "Google Drive disconnected"}), 200