import os

from flask import current_app
from google_auth_oauthlib.flow import Flow


def build_google_auth_flow(state: str | None = None):
    client_secrets_file = current_app.config["GOOGLE_OAUTH_CLIENT_SECRETS_FILE"]
    redirect_uri = current_app.config["GOOGLE_OAUTH_REDIRECT_URI"]
    scopes = current_app.config["GOOGLE_OAUTH_SCOPES"]

    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError(
            f"oauth client secrets file not found: {client_secrets_file}"
        )

    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow